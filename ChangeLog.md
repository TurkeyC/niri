## virtual pointer overlay skip

Virtual pointer events (e.g. from baspark click-through overlays) now skip the `Overlay` wlr-layer-shell layer so they reach the window below.

### Modified files

**src/input/mod.rs**
- Added `VirtualPointerInputBackend` import
- `on_pointer_motion_absolute`: added `'static` bound on `I` to enable `TypeId` dispatch
- Virtual pointer inputs use `contents_under_skip_overlay` instead of `contents_under` to bypass overlay layer surfaces

**src/niri.rs**
- Added `contents_under_skip_overlay()` — identical to `contents_under()` but omits the `Layer::Overlay` layer check, letting input pass through to layers below

---

## added `GetCursorPos` IPC command

A new IPC command `GetCursorPos` is added to query the current mouse cursor position in logical coordinates.

### Modified files

**niri-ipc/src/lib.rs** (IPC type definitions)
- Added `GetCursorPos` variant to `Request` enum
- Added `CursorPos(CursorPos)` variant to `Response` enum
- Added `CursorPos` struct with `x: f64` and `y: f64` fields

**src/cli.rs** (CLI subcommand)
- Added `GetCursorPos` variant to `Msg` enum

**src/ipc/client.rs** (IPC client — CLI→request mapping and response output)
- Added `CursorPos` to `niri_ipc` imports
- Added `Msg::GetCursorPos => Request::GetCursorPos` in message mapping
- Added `Msg::GetCursorPos` response handler with JSON and text output formats

**src/ipc/server.rs** (IPC server — request processing)
- Added `CursorPos` to `niri_ipc` imports
- Added `Request::GetCursorPos` handler in `process()`
- Uses `insert_idle` pattern (matching existing convention) to safely access `state.niri.seat.get_pointer().unwrap().current_location()` on the compositor event loop

### Safety notes

- Pointer position is obtained via `PointerHandle::current_location()`, which returns a `Copy` type (`Point<f64, Logical>`), avoiding any borrow conflicts.
- The `insert_idle` pattern is standard practice in niri's IPC server for accessing compositor state (same pattern used by `Layers`, `PickWindow`, `PickColor` etc.).
