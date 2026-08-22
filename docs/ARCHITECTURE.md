# Architecture

Escrow pakai `TreeMap` untuk simpan data per id, `u256` untuk amount.

Flow: buyer fund → seller kirim → buyer confirm atau dispute → resolve cek bukti.

Testing: direct (mock) dan integration (GLSim).
