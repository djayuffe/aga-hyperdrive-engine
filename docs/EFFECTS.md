# Effects

## Implemented effects

- Deterministic full-screen art, logo, music and Paula-loop generation.
- Generated AGA 24-bit plasma palette.
- Generated Copper-gradient table.
- Generated tunnel reciprocal table.
- Live Copper slot updater in the assembly frame loop.
- FS-UAE A1200 test displays the generated 320×256 art through Copper-patched bitplane pointers, starts audio DMA and remains running until left mouse exit.
- **Copper lattice plasma** — live AGA high/low colour slots driven by scene speed, tunnel phase and music pulse.
- **Tunnel layer** — generated reciprocal table sampled by `Effect_TunnelLayer` for camera/depth control.
- **Sprite orb layer** — eight hardware sprite pointers and an animated first-orb position are patched at startup/runtime.
- **Music event bus** — `Music_EventBus` turns tracker ticks into a decaying pulse that modulates visual phases.
- **Scene sequencer** — `Scene_Update` cycles scene speed/tunnel/orb parameters every 256 frames.
- **Generated composite screen** — deterministic logo, aurora/plasma field, wire tunnel, shaded orbs, status panel and floor bars are packed as four planar bitplanes.
- **Paula runtime audio** — generated signed 8-bit loop is replayed on AUD0 with clean shutdown.

## Completion boundary

This repository now ships a complete bootable/demoable engine pass with deterministic source-generated art, tables, music data, audio loop, executable, floppy-turbo staging, manifest validation and emulator screenshots. Future changes can add more scenes, but the current effect graph is fully wired rather than a scaffold.
