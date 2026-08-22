# Architecture — GenLayer Hello

## Kenapa Intelligent Contract?

Escrow tradisional butuh arbiter manusia. Di GenLayer, arbiter-nya adalah LLM + validator yang menjalankan equivalence principle.

- **Leader** call LLM + web.get untuk menilai bukti
- **Validator** reproduce atau cek JSON winner sama (buyer/seller) — tidak perlu byte identik

## Storage

- `TreeMap[u256, Escrow]` untuk escrow by id
- `u256` untuk amount/fee (bukan int Python)
- `Address` untuk buyer/seller

## Testing

- `tests/direct` mock web/LLM
- `tests/integration` pakai GLSim untuk konsensus

## Deploy

Lihat README.
