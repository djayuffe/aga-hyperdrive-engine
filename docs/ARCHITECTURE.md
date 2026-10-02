# Architecture

AGA Hyperdrive Engine is split into deterministic generation tools and a small 68000 assembly runtime.

## Runtime modules

- `Startup_AGAGate` isolates chipset detection.
- `Engine_Init` owns the custom-chip setup and installs the Copper list.
- `Effect_Init` and `Effect_Frame` are the effect graph entry points.
- `Effect_CopperLattice` rewrites AGA high/low colour slots from a generated 24-bit table.
- `Effect_BitplaneWarp` modulates `BPLCON1` for real hardware scroll/shear movement.
- `Effect_CopperLattice`, `Effect_TunnelLayer`, `Effect_SpriteOrbLayer`, `Effect_BlitterVectorPulse`, `Scene_Update` and `Music_EventBus` form the per-frame effect graph.
- `Screen_Init` is intentionally light because the full-height planar screen is source-generated and included as `assets/screen.raw`.
- `Music_Init` starts Paula AUD0 playback from `assets/audio_loop.raw`; `Music_Tick` drives the visual event pulse.
- The main loop is persistent and exits only on left mouse, matching demo/cracktro behaviour instead of auto-closing during boot smoke tests.

## Data flow

```text
tools/generate_assets.py
 ├─ logo.raw / logo_preview.png
 ├─ screen.raw / screen_preview.png
 ├─ hyperdrive.mod
 ├─ audio_loop.raw
 ├─ sprite_orbs.bin / sprite_path.bin
 ├─ plasma_palette.bin
 ├─ copper_gradient.bin
 └─ tunnel.bin

src/main.s
 ├─ Copper setup
 ├─ effect frame loop
 ├─ generated binary includes
 └─ classic hunk executable
```

## Hardware plan

The engine is designed around AGA PAL:

- 320×256 low-resolution display.
- Four bitplanes as the baseline compositing surface.
- AGA colour writes through `BPLCON3` high/low nibble selection.
- Copper-controlled effect slots for per-line 24-bit colour motion.
- Runtime `BPLCON1` scroll/shear for planar warp motion.
- Hardware sprite DMA with generated 16-line orb images and live control words.
- Blitter DMA workload for a vector scratch surface.

## Floppy turbo mode

`make floppy-turbo` creates `build/floppy_turbo`, a minimal floppy-style staging directory with:

- `S/Startup-Sequence`
- `aga_hyperdrive_engine`
- minimal `C`, `DEVS` and `LIBS` directories

The startup sequence launches the engine directly so minimal AROS/Kickstart boot environments do not abort on missing shell helper commands. If `xdftool` is installed, the build also emits `build/aga_hyperdrive_turbo.adf`.
