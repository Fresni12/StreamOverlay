# LoL Series Overlay

A lightweight stream overlay for League of Legends spectator broadcasts. Displays team abbreviations, seedings, and series progress (BO1/BO3/BO5) on top of the native LoL scoreboard. Built for OBS/Streamlabs.

---

## Files

| File | Description |
|---|---|
| `overlay.html` | The transparent browser source added to OBS/Streamlabs |
| `controller.html` | The control panel opened in Chrome to manage the series |
| `server.py` | Local relay server that syncs state between the two |

---

## Setup

### 1. Start the relay server
The server bridges the controller (Chrome) and the overlay (Streamlabs/OBS), which run in separate browser instances and can't share memory directly.

Open a terminal in the project folder and run:

```bash
python server.py
```

Keep this terminal open while streaming. Python 3 is required (pre-installed on Windows 10/11).

### 2. Add the overlay to OBS / Streamlabs

- Add a new **Browser Source**
- Set the local file path to `overlay.html`
- Set resolution to **1920 × 1080**
- Paste this into **Custom CSS**:
  ```css
  body { background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }
  ```

### 3. Open the controller

Open `controller.html` in **Chrome**. This is where you manage the series live.

---

## Configuration

At the top of `overlay.html` there are three constants you can edit:

```js
const SCALE       = 1.3;  // Overall badge size. 1.0 = default, 1.5 = 50% bigger
const BADGE_LEFT  = 350;  // Right edge of the left badge (px from left of screen)
const BADGE_RIGHT = 350;  // Left edge of the right badge (px from right of screen)
```

Adjust `BADGE_LEFT` and `BADGE_RIGHT` to position the badges just outside the LoL scoreboard on your setup. The badges always grow away from the scoreboard so long names won't overlap it.

---

## Controls

### Controller UI
| Button | Action |
|---|---|
| 🏆 Left / Right | Award a game win to that team |
| ⇄ Swap Sides | Swap which team is on which side |
| ↩ Undo | Revert the last action |
| ↺ Reset Scores | Reset both scores to 0 |
| ✕ New Series | Go back to the setup screen |

### Keyboard Shortcuts
| Shortcut | Action |
|---|---|
| `Ctrl+Shift+←` | Left team wins a game |
| `Ctrl+Shift+→` | Right team wins a game |
| `Ctrl+Shift+S` | Swap sides |
| `Ctrl+Shift+Z` | Undo |
| `Ctrl+Shift+R` | Reset scores |
| `Ctrl+Shift+T` | New series |

---

## Features

- **BO1 / BO3 / BO5** format support
- **Team seeding** — optional, e.g. `#1`. Type just `1` and it displays as `#1` automatically
- **Win banner** — animated overlay shown on series/match completion
- **Undo history** — step back through any number of actions
- **Server health indicator** — controller shows live status of the relay server
- **No letter limit** on team abbreviations
