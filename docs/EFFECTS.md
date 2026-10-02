# Effects

## Implemented foundation

- Deterministic logo and music generation.
- Generated AGA 24-bit plasma palette.
- Generated Copper-gradient table.
- Generated tunnel reciprocal table.
- Live Copper slot updater in the assembly frame loop.

## Next hardware-maximising effects

1. **Copper lattice plasma** — two interleaved AGA colour channels, phase-shifted every frame.
2. **Blitter vector tunnel** — clipped line spans and reciprocal camera motion.
3. **Sprite orb layer** — eight hardware sprites reused by depth band.
4. **Music event bus** — MOD row events mapped to effect parameters.
5. **Scene sequencer** — fixed-point interpolation of effect parameters per scene.
