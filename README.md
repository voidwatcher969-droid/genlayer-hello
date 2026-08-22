# GenLayer Hello — Escrow Demo

Demo escrow sederhana untuk GenLayer Builder Program Season 1.

## Latar Belakang

Transaksi antar wallet seringkali butuh penengah. Di GenLayer, kontrak bisa panggil data eksternal (resi, tracking) untuk bantu putuskan sengketa tanpa perantara manual.

Project ini contoh escrow: pembeli lock dana, penjual kirim barang, kalau ada sengketa kontrak cek bukti yang ada di URL yang diberikan.

## Fitur

- `create_escrow` — buat escrow baru dengan bukti URL
- `fund` — pembeli lock GEN
- `confirm_delivery` — pembeli konfirmasi → dana cair ke penjual
- `raise_dispute` — salah satu pihak ajukan sengketa
- `resolve_dispute` — kontrak cek bukti via web + penilaian, lalu bayarkan ke pemenang
- Fee 0.5% untuk owner

## Struktur

```
contracts/
  escrow.py      # kontrak utama
  hello.py       # contoh simpel
frontend/
  index.html     # demo UI
docs/
  ARCHITECTURE.md
```

## Cara Deploy

### StudioNet (gasless)
```bash
genlayer network set studionet
genlayer account create --name demo
genlayer deploy contracts/escrow.py --network studionet
```

### Bradbury Testnet
```bash
genlayer network set bradbury
# isi GEN dari https://testnet-faucet.genlayer.foundation (100 GEN / 7 hari)
genlayer deploy contracts/escrow.py --network bradbury
```

## Testing

```bash
genvm-lint check contracts/escrow.py --json
pytest tests/direct -v
gltest tests/integration -v -s
```

## Link

- Repo: https://github.com/voidwatcher969-droid/genlayer-hello
- Portal: https://portal.genlayer.foundation/?ref=CS1PFL8B
- Faucet: https://testnet-faucet.genlayer.foundation
