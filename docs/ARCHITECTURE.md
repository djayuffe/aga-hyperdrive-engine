# Architecture

AGA Hyperdrive Engine is split into deterministic generation tools and a small 68000 assembly runtime.

## Runtime modules

- `Startup_AGAGate` isolates chipset detection.
- `Engine_Init` owns the custom-chip setup and installs the Copper list.
- `Effect_Init` and `Effect_Frame` are the effect graph entry points.
- `Effect_UpdateCopperGradient` rewrites AGA high/low colour slots from a generated 24-bit table.
- `Music_Init` and `Music_Tick` reserve the music control surface.

## Data flow

```text
tools/generate_assets.py
 ├─ logo.raw / logo_preview.png
 ├─ hyperdrive.mod
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
- Blitter line/fill layer for vector and tunnel effects.
- Hardware sprites for high-priority glow/orb layers.
