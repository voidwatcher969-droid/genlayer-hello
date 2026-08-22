# { "Depends": "py-genlayer:0.1.0" }
"""
GenLayer Intelligent Escrow — demo untuk Builder Program

Flow ini dibuat dengan komentar yang cukup detail. Logika intinya: escrow + dispute yang diselesaikan via pengecekan web + penilaian.

Catatan: ini contoh edukasi, bukan untuk mainnet tanpa audit.
"""

from genvm import *
import json

# Storage types — jangan pakai dict/list mentah
@dataclass
class Escrow:
    buyer: Address
    seller: Address
    amount: u256
    state: str  # "created" | "funded" | "disputed" | "resolved"
    evidence_url: str
    winner: Address | None = None

class EscrowContract(Contract):
    owner: Address
    next_id: u256 = u256(1)
    escrows: TreeMap[u256, Escrow]
    fee_bps: u256 = u256(50)  # 0.5% fee contoh

    def __init__(self, owner: Address):
        self.owner = owner
        self.next_id = u256(1)
        # fee bisa di-update owner nanti
        self.fee_bps = u256(50)

    @call
    def get_escrow(self, escrow_id: u256) -> Escrow:
        assert escrow_id in self.escrows, "NOT_FOUND"
        return self.escrows[escrow_id]

    @call
    def list_escrows(self, limit: u256 = u256(10)) -> DynArray[Escrow]:
        out: DynArray[Escrow] = DynArray[Escrow]()
        cnt = u256(0)
        for eid, esc in self.escrows.items():
            if cnt >= limit:
                break
            out.append(esc)
            cnt += u256(1)
        return out

    @write
    def create_escrow(self, seller: Address, evidence_url: str) -> u256:
        assert seller != Address(0), "SELLER_ZERO"
        # evidence_url bisa berupa link resi, chat log, atau IPFS
        assert len(evidence_url) > 10, "URL_TOO_SHORT"
        eid = self.next_id
        self.next_id += u256(1)
        self.escrows[eid] = Escrow(
            buyer=msg.sender,
            seller=seller,
            amount=u256(0),
            state="created",
            evidence_url=evidence_url,
            winner=None,
        )
        emit("EscrowCreated", eid, msg.sender, seller)
        return eid

    @write
    @payable
    def fund(self, escrow_id: u256):
        esc = self.escrows[escrow_id]
        assert esc.state == "created", "STATE_NOT_CREATED"
        assert msg.sender == esc.buyer, "NOT_BUYER"
        assert msg.value > u256(0), "ZERO_VALUE"
        # simpan amount dari msg.value
        esc.amount = msg.value
        esc.state = "funded"
        self.escrows[escrow_id] = esc
        emit("Funded", escrow_id, msg.value)

    @write
    def confirm_delivery(self, escrow_id: u256):
        esc = self.escrows[escrow_id]
        assert esc.state == "funded", "NOT_FUNDED"
        assert msg.sender == esc.buyer, "NOT_BUYER"
        # transfer ke seller (minus fee)
        fee = esc.amount * self.fee_bps // u256(10000)
        payout = esc.amount - fee
        # send ke seller
        send(esc.seller, payout)
        if fee > u256(0):
            send(self.owner, fee)
        esc.state = "resolved"
        esc.winner = esc.seller
        self.escrows[escrow_id] = esc
        emit("Resolved", escrow_id, esc.seller)

    @write
    def raise_dispute(self, escrow_id: u256, reason: str):
        esc = self.escrows[escrow_id]
        assert esc.state == "funded", "NOT_FUNDED"
        assert msg.sender in (esc.buyer, esc.seller), "NOT_PARTY"
        assert len(reason) > 5, "REASON_SHORT"
        esc.state = "disputed"
        self.escrows[escrow_id] = esc
        emit("Disputed", escrow_id, msg.sender, reason)

    # === Intelligent resolution ===
    # Leader akan call LLM + web, validator akan reproduce atau cek equivalence

    def _llm_judge(self, evidence_url: str, buyer: Address, seller: Address) -> Address:
        # Coba ambil tracking dulu (web)
        tracking = ""
        try:
            # web.get bisa gagal — kita tangkap sebagai EXTERNAL
            resp = web.get(evidence_url, timeout=5)
            tracking = resp.text[:1000] if hasattr(resp, "text") else str(resp)[:1000]
        except Exception as e:
            tracking = f"EXTERNAL: web.get failed {e}"

        # Prompt terstruktur — minta JSON
        prompt = f"""You are an escrow judge for GenLayer.
Evidence URL: {evidence_url}
Tracking snippet: {tracking}
Buyer: {buyer}
Seller: {seller}

Task: decide winner based on delivery proof.
Rules:
- If tracking shows "delivered" or "received" → seller wins
- If tracking shows "not found", "returned", or empty → buyer wins
- If ambiguous → seller wins if evidence URL reachable (200), else buyer

Return JSON only: {{"winner": "buyer" or "seller", "reason": "short reason", "confidence": 0.0-1.0}}
"""
        try:
            out = llm.chat(prompt, model="gpt-4o-mini", temperature=0.2)
            # bersihkan markdown ```json
            txt = out.strip()
            if txt.startswith("```"):
                txt = txt.split("```")[1]
                if txt.startswith("json"):
                    txt = txt[4:]
                txt = txt.strip()
            data = json.loads(txt)
            w = data.get("winner","").lower()
            if w == "buyer":
                return buyer
            if w == "seller":
                return seller
            # fallback
            return seller
        except Exception as e:
            # Prefix deterministic untuk equivalence
            if "LLM_ERROR" in str(e):
                return seller
            return seller

    @write
    def resolve_dispute(self, escrow_id: u256):
        esc = self.escrows[escrow_id]
        assert esc.state == "disputed", "NOT_DISPUTED"
        assert msg.sender in (esc.buyer, esc.seller, self.owner), "NOT_AUTH"

        # Panggil LLM + web — ini non-deterministik, jadi equivalence via custom validator
        winner = self._llm_judge(esc.evidence_url, esc.buyer, esc.seller)

        # payout
        fee = esc.amount * self.fee_bps // u256(10000)
        payout = esc.amount - fee
        send(winner, payout)
        if fee > u256(0):
            send(self.owner, fee)

        esc.state = "resolved"
        esc.winner = winner
        self.escrows[escrow_id] = esc
        emit("Resolved", escrow_id, winner)

    # Untuk testing direct (mock LLM)
    @write
    def set_fee(self, new_bps: u256):
        assert msg.sender == self.owner, "NOT_OWNER"
        assert new_bps <= u256(500), "FEE_TOO_HIGH"  # max 5%
        self.fee_bps = new_bps
