# AGA Hyperdrive Engine

**AGA Hyperdrive Engine** is a new-from-scratch Amiga AGA effects engine aiming for state-of-the-art PAL Amiga 1200/4000 visuals while staying original, reproducible and hardware-conscious.

The first revision establishes the engine spine: deterministic assets, generated music, generated 24-bit AGA palettes, Copper effect slots, a frame loop, validation tooling and a classic hunk build path. The intent is to push AGA hardware with layered Copper, blitter, sprite and music systems rather than being a single hard-coded intro.

![Generated logo preview](docs/screenshots/aga-hyperdrive-logo-preview.png)

## FS-UAE test run

![AGA Hyperdrive Engine running in FS-UAE](docs/screenshots/fsuae-testrun.png)

## Design goals

- Maximise AGA capability with 24-bit Copper gradients, palette banking, sprite layers and blitter/vector workloads.
- Keep the CPU path 68000-compatible where practical, with a clear route for 68020/A1200 optimisations.
- Make every generated asset reproducible from source.
- Build a reusable effect graph rather than one-off scene code.
- Keep music in-repo: generated ProTracker-compatible module data with bass, lead, glass, kick, snare and hat instruments.
- Validate structure, assets and release manifests on the host.

## Engine layers

| Layer | Purpose | Current state |
| --- | --- | --- |
| Startup | AGA gate, OS-safe entry/exit | isolated gate and clean structure |
| Copper | Display setup and AGA colour slots | 32 live 24-bit slots plus generated gradients |
| Bitmap | Four-plane 320-wide logo/screen storage | deterministic planar logo asset |
| Plasma | 256-colour 24-bit AGA ramp | generated binary table |
| Tunnel | Reciprocal camera/projection table | generated binary table |
| Music | Four-channel MOD data | generated `assets/hyperdrive.mod` |
| Validation | Asset/source/manifest sanity | `make validate`, reproducibility, manifest |

## Build

```sh
make validate
make verify-repro
make
make floppy-turbo
```

The full executable build requires `vasmm68k_mot` on `PATH` or at `tools/bin/vasmm68k_mot`.

Output:

```text
build/aga_hyperdrive_engine
build/floppy_turbo/
build/aga_hyperdrive_turbo.adf   # optional, only when xdftool exists
```

## Generate assets

```sh
make assets
python3 tools/generate_assets.py
python3 tools/gen_tables.py plasma_palette
python3 tools/gen_tables.py copper_gradient
python3 tools/gen_tables.py tunnel
```

Generated assets:

- `assets/logo.raw`
- `assets/logo_preview.png`
- `assets/hyperdrive.mod`
- `assets/plasma_palette.bin`
- `assets/copper_gradient.bin`
- `assets/tunnel.bin`

## Run target

Use FS-UAE/WinUAE/Amiberry with an A1200 or A4000 AGA PAL configuration. The current executable is a foundation/smoke-test engine build that displays the generated logo through real Copper bitplane pointers and live AGA colour-slot updates. It stays running until the left mouse button is pressed. The next milestones are full chip-RAM rebasing, hardware-confirmed AGA detection, blitter vector layer, sprite multiplexer and scene sequencer.

## Validation

```sh
make validate
python3 tools/verify_repro.py
python3 tools/make_manifest.py
shasum -a 256 -c MANIFEST.sha256
```

## Original effect roadmap

- Hyperdrive plasma lattice: per-line AGA colour writes plus sub-frame palette phase modulation.
- Blitter spline tunnel: reciprocal-table camera, line spans and collision-safe clipping.
- Sprite energy orbs: depth-sorted hardware sprites with palette cycling.
- Morphing logo material: Copper glint, per-row scroll and dynamic colour-bank swaps.
- Music-reactive scene graph: MOD row/tick events drive plasma intensity, tunnel speed and sprite bursts.

## License

GPL-3.0-or-later. See `LICENSE`.
