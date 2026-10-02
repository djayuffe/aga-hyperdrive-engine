# Music

`tools/generate_assets.py` writes two deterministic music assets:

- `assets/hyperdrive.mod`, a four-channel ProTracker-style reference module.
- `assets/audio_loop.raw`, a signed 8-bit Paula-ready loop that the runtime plays on AUD0.

Current instruments:

- `SUBBASS`
- `HYPERSAW`
- `GLASS`
- `KICK`
- `SNARE`
- `HAT`

The runtime starts the raw Paula loop during `Music_Init`, sets the period/length/volume registers, enables AUD0 DMA and mutes the channel during shutdown. `Music_Tick` still provides the row/tick-style event pulse used by the visual effect graph, so visuals and sound share deterministic timing even without loading an external tracker replay routine.
