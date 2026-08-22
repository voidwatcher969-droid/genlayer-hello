# GenLayer Hello — Intelligent Escrow Demo

> **Project for GenLayer Builder Program — Season 1**
> A minimal but complete Intelligent Contract example that showcases GenLayer's **Intelligent Contracts** + **Equivalence Principle** for dispute resolution in peer-to-peer escrow.

---

## 1. Latar Belakang

Di ekonomi agentic, banyak transaksi terjadi antar AI agent tanpa perantara. Masalah utama: bagaimana menyelesaikan sengketa ketika dua agent tidak sepakat? GenLayer menjawab dengan **Intelligent Contracts** — kontrak yang bisa memanggil LLM dan mengakses web untuk verifikasi, lalu validator mencapai konsensus via *equivalence* (bukan determinisme byte-per-byte).

Project ini adalah **demo escrow** sederhana: pembeli lock dana, penjual kirim barang, dan jika sengketa, kontrak memanggil LLM untuk menilai bukti (foto resi, chat log, tracking number) yang diambil via `web.get`.

## 2. Fitur

- **Escrow lifecycle**: `create_escrow` → `fund` → `confirm_delivery` / `raise_dispute` → `resolve`
- **Intelligent resolution**: `resolve_dispute` memanggil `llm.chat` dengan prompt terstruktur untuk klasifikasi `EXPECTED` vs `EXTERNAL` error, + `web.get` untuk cek resi di `https://api.example.com/track/{id}`
- **Equivalence**: leader & validator fungsi terpisah — leader call LLM, validator reproduce atau gunakan `strict_eq=False` untuk output fuzzy
- **Storage aman**: pakai `TreeMap`, `u256`, `String` dari `genvm`, bukan `dict`/`list` Python mentah
- **Events**: `EscrowCreated`, `Disputed`, `Resolved`

## 3. Arsitektur

```
contracts/
  escrow.py      # Intelligent Contract utama (700+ LOC)
  hello.py       # Contoh sederhana (untuk testing)
frontend/
  index.html     # Demo UI vanilla JS + genlayer-js
  app.js         # createClient, writeContract, readContract
tests/
  direct/test_escrow.py   # Gl direct tests (mock LLM/web)
  integration/test_escrow.py # Gltest dengan konsensus
```

Flow:
```
Buyer --fund(1 GEN)--> Escrow --confirm--> Seller receives
                \--dispute--> LLM(web) --> Validator consensus --> Winner
```

## 4. Cara Deploy

### Prasyarat
- Node >= 18, `npm install -g genlayer`
- `pip install genvm-linter genlayer-test`
- Faucet: https://testnet-faucet.genlayer.foundation (100 GEN / 7 hari, GitHub auth)

### Deploy ke StudioNet (gasless)
```bash
genlayer network set studionet
genlayer account create --name demo
genlayer deploy contracts/escrow.py --network studionet
# catat address 0x...
genlayer call 0x... --method get_escrow --args '[1]'
```

### Deploy ke Bradbury Testnet
```bash
genlayer network set bradbury
# isi GEN dari faucet
genlayer deploy contracts/escrow.py --network bradbury
```

## 5. Testing

```bash
# lint
genvm-lint check contracts/escrow.py --json

# direct (mock LLM)
pytest tests/direct -v

# integration (butuh Docker + sim)
gltest tests/integration -v -s
```

## 6. Evidence untuk GenLayer Portal

- **GitHub Repo:** https://github.com/voidwatcher969-droid/genlayer-hello
- **Contract (Studio):** https://studio.genlayer.com/?import-contract=0x0000000000000000000000000000000000000000 (ganti setelah deploy)
- **Explorer:** https://explorer-asimov.genlayer.com/address/0x... (setelah deploy di Asimov)
- **X Post:** https://x.com/voidwatcher969/status/0000000000000000000 (demo thread)

## 7. Roadmap

- [x] Escrow core + LLM resolver
- [ ] Frontend dengan `genlayer-js` (createClient, chains.bradbury)
- [ ] Multi-escrow batch + fee split
- [ ] Integrasi `x402` untuk payment agentic

## 8. Lisensi

MIT — dibuat untuk edukasi Builder Program. Bukan financial advice.

---

**Referral:** https://portal.genlayer.foundation/?ref=CS1PFL8B
**Builder:** voidwatcher969-droid (0xc4D0FE1Ab1B4405e1509c166d933D98A2f9c69F6)
**Kontak:** voidwatcher969@gmail.com
