# LoL Series Overlay

A lightweight stream overlay for League of Legends spectator broadcasts. Displays team abbreviations, seedings, and series progress (BO1/BO3/BO5) on top of the native LoL scoreboard, with live in-game data including rune matchups, head-to-head stats, and objective buff timers. Built for OBS/Streamlabs.

---

## Files

| File | Description |
|---|---|
| `overlay.html` | The transparent browser source added to OBS/Streamlabs |
| `controller.html` | The control panel opened in Chrome to manage the series |
| `server.py` | Local relay server that syncs state between the two |
| `keybinds.json` | User-editable keyboard shortcut configuration |

---

## Setup

### 1. Start the relay server
The server bridges the controller (Chrome) and the overlay (Streamlabs/OBS), which run in separate browser instances and can't share memory directly. It also proxies calls to the League Live Client API to avoid CORS issues.

Open a terminal in the project folder and run:

```bash
python server.py
```

Keep this terminal open while streaming. Python 3 is required (pre-installed on Windows 10/11).

> **Optional — global hotkeys:** Install the `keyboard` package to enable system-wide hotkeys that work even when the controller window isn't focused:
> ```bash
> pip install keyboard
> ```
> Without it the hotkeys still work inside the controller browser tab, just not globally.

### 2. Add the overlay to OBS / Streamlabs

Two options:

**File path (default):**
- Add a new **Browser Source**
- Set the local file path to `overlay.html`

**Via the relay server (alternative):**
- Add a new **Browser Source**
- Set the URL to `http://localhost:8765/overlay`

Either way, set the resolution to **1920 × 1080** and paste this into **Custom CSS**:
```css
body { background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }
```

### 3. Open the controller

Open `controller.html` in **Chrome**. This is where you manage the series live.

---

## Configuration

### Overlay scaling (`overlay.html`)

At the top of `overlay.html` there are constants you can edit:

```js
const SCALE         = 1.3;   // Overall badge size. 1.0 = default, 1.5 = 50% bigger
const MATCHUP_SCALE = 1.87;  // Size of the matchup/stats panel
const STRIP_SCALE   = 1.0;   // Size of the champion buff strip slots
const BADGE_LEFT    = 480;   // Right edge of the left badge (px from left of screen)
const BADGE_RIGHT   = 480;   // Left edge of the right badge (px from right of screen)
```

Adjust `BADGE_LEFT` and `BADGE_RIGHT` to position the badges just outside the LoL scoreboard on your setup. The badges always grow away from the scoreboard so long names won't overlap it.

### Keyboard shortcuts (`keybinds.json`)

All keyboard shortcuts are configured in `keybinds.json`. Edit this file in any text editor to change a shortcut — no code editing required. The server must be running for the controller to pick up the file; changes take effect immediately on reload (the controller has a **↻ reload** button next to the shortcuts panel, or just refresh the page).

```json
{
  "leftWins":    "ctrl+shift+left",
  "rightWins":   "ctrl+shift+right",
  "swapSides":   "ctrl+shift+s",
  "undo":        "ctrl+shift+z",
  "resetScores": "ctrl+shift+r",
  "newSeries":   "ctrl+shift+t",

  "roleTop":     "ctrl+alt+1",
  "roleJungle":  "ctrl+alt+2",
  "roleMid":     "ctrl+alt+3",
  "roleBot":     "ctrl+alt+4",
  "roleSupport": "ctrl+alt+5"
}
```

**Format:** separate modifiers and the final key with `+`, all lowercase.

| Type | Values |
|---|---|
| Modifiers | `ctrl` `shift` `alt` `meta` (Win/Cmd) |
| Letters | `a`–`z` |
| Digits | `0`–`9` |
| Arrows | `left` `right` `up` `down` |
| Function keys | `f1`–`f12` |
| Other | `enter` `escape` `space` `backspace` `delete` `tab` |

**Examples:** `ctrl+shift+left` · `ctrl+alt+f5` · `alt+q` · `ctrl+shift+alt+r`

The `_help` key already in the file is a comment and is ignored by the application. If `keybinds.json` is missing or unreadable, both the controller and the server fall back to the default shortcuts shown above.

---

## Controls

### Controller UI

| Button | Action |
|---|---|
| 🏆 Left / Right | Award a game win to that team |
| ⇄ Swap Sides | Swap which team is on which side |
| ↩ Undo | Revert the last action |
| ↺ Reset Scores | Reset both scores to 0 |
| ◉ Hide / Show Overlay | Toggle all overlay elements on or off |
| ✕ New Series | Go back to the setup screen |
| ↻ Fetch | Pull live champion, rune and stat data from the running game |
| Role buttons (centre column) | Select a role to display the stats panel on the overlay; click the same role again to dismiss it |
| Role strip (far left) | Shortcut buttons for each role; shows the configured key from `keybinds.json` and highlights the active role |
| ✕ Hide (sidebar footer) | Clear the active role and hide the stats panel |

### Objective Buttons
Four buttons in the controller sidebar let you manually track Baron and Elder Dragon buffs for either team. Activating one starts a countdown timer visible on the overlay. A live timer badge appears on the button itself while the buff is running. The buff auto-expires when the timer reaches zero. Activating the same button again while it is running cancels it early.

| Buff | Duration |
|---|---|
| Baron | 3:00 |
| Elder Dragon | 2:30 |

While any buff is active, the controller automatically re-fetches live game data every 4 seconds so champion death states and stats stay current.

### Keyboard Shortcuts

Shortcuts are loaded from `keybinds.json` and displayed live in the controller's **Keyboard Shortcuts** panel. Click **↻ reload** in that panel to pick up changes to `keybinds.json` without refreshing the page. The table below shows the defaults.

| Shortcut | Action |
|---|---|
| `Ctrl+Shift+←` | Left team wins a game |
| `Ctrl+Shift+→` | Right team wins a game |
| `Ctrl+Shift+S` | Swap sides |
| `Ctrl+Shift+Z` | Undo |
| `Ctrl+Shift+R` | Reset scores |
| `Ctrl+Shift+T` | New series |
| `Ctrl+Alt+1` | Toggle Top stats panel |
| `Ctrl+Alt+2` | Toggle Jungle stats panel |
| `Ctrl+Alt+3` | Toggle Mid stats panel |
| `Ctrl+Alt+4` | Toggle Bot stats panel |
| `Ctrl+Alt+5` | Toggle Support stats panel |

`Ctrl+Alt+1–5` work inside the controller browser tab at all times. If the `keyboard` Python package is installed they also work as **global system hotkeys** while the server is running, so you can control the overlay without switching windows.

---

## Features

### Series management
- **BO1 / BO3 / BO5** format support
- **Team seeding** — optional, e.g. `#1`. Type just `1` and it displays as `#1` automatically
- **Win banner** — animated overlay shown on series/match completion, with the winner's name, score, and a "Series Victory" / "Match Victory" label depending on format
- **Undo history** — step back through any number of actions
- **Server health indicator** — controller shows a live coloured dot and status label for the relay server connection
- **No letter limit** on team abbreviations

### Live game data (requires game to be running)
Clicking **↻ Fetch** in the controller pulls live data from the League Live Client API and populates the matchup sidebar. Fetching also happens automatically when you activate a role or when a buff is active. The server additionally runs a background loop that silently refreshes the data every 10 seconds while a stats panel is open, so values update without any manual action.

Gold values are calculated using full item costs sourced from DDragon (not the Live Client's recipe-delta price), which gives accurate item gold totals.

The controller sidebar shows for each player:
- **Champion portrait** (loaded from DDragon)
- **Champion name**
- **K/D/A and CS** once live data is fetched
- **Rune icons** — keystone, secondary tree icon, and stat shard icons inline below the portrait

Players are always sorted by role (Top → Jungle → Mid → Bot → Support).

### Stats panel (overlay)
Selecting a role in the controller triggers a three-phase animated sequence on the overlay:

1. **Phase 1 — Intro title**: "HEAD TO HEAD" fades in with the role name and icon
2. **Phase 2 — VS matchup**: Champion portraits for both players appear with their summoner names and a VS separator
3. **Phase 3 — Stats reveal**: The intro overlay fades away, exposing the full stat panel underneath

The revealed stats panel contains:
- Champion portraits and summoner names for both players
- **Rune columns** flanking the stats — keystone and secondary tree icons for each side, colour-coded by team
- **Head-to-head stat bars** for LVL, KDA, Vision Score, Kill Participation, and Item Gold — each row shows both values with a proportional bar; the leading player's value is highlighted in their team colour

Clicking the same role button again closes the panel. The panel refreshes its values live while open without replaying the intro animation.

### Matchup panel (overlay)
A separate rune-focused panel is available alongside the stats panel. It shows:
- An animated VS intro with large champion portraits and summoner names
- Full rune pages for both players: keystone (with primary tree colour), secondary tree, and all three stat shards
- Keystone and tree names displayed in their respective tree colours

The matchup and stats panels are mutually exclusive — activating one dismisses the other.

### Objective buff tracking (overlay)

**Buff panels** appear at the top of the screen when a buff is activated:
- Positioned on the left (blue team) or right (red team) side of the screen
- Show the team abbreviation, a live countdown timer, and a draining progress bar
- Baron panel uses purple, Elder panel uses orange
- Both panels can be visible simultaneously if each team holds a different buff

**Champion buff strips** run along the left and right edges of the screen for the duration of the buff:
- Blue team slots appear on the left edge, red team slots on the right
- **Baron buff**: a pulsing purple square border animates around each champion slot
- **Elder buff**: a pulsing orange vertical line runs alongside each slot
- Both effects can appear on the same strip if a team holds both buffs
- Slots for **dead players** automatically suppress their border and line, restoring them when the player respawns
- All slots on a strip share a synchronised animation phase so they pulse in unison
