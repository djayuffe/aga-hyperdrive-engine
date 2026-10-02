# Effects

## Implemented foundation

- Deterministic logo and music generation.
- Generated AGA 24-bit plasma palette.
- Generated Copper-gradient table.
- Generated tunnel reciprocal table.
- Live Copper slot updater in the assembly frame loop.
- FS-UAE A1200 smoke test displays the generated logo through Copper-patched bitplane pointers and remains running until left mouse exit.
- **Copper lattice plasma** — live AGA high/low colour slots driven by scene speed, tunnel phase and music pulse.
- **Tunnel layer** — generated reciprocal table sampled by `Effect_TunnelLayer` for camera/depth control.
- **Sprite orb layer** — eight hardware sprite pointers and an animated first-orb position are patched at startup/runtime.
- **Music event bus** — `Music_EventBus` turns tracker ticks into a decaying pulse that modulates visual phases.
- **Scene sequencer** — `Scene_Update` cycles scene speed/tunnel/orb parameters every 256 frames.

## Remaining expansion work

The remaining work is depth and polish rather than missing architecture: replace the placeholder sprite bitmap with shaded orb art, add actual blitter line/fill spans on top of the tunnel depth value, and wire the generated MOD replay to Paula DMA.
