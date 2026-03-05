#!/usr/bin/env python3
"""
LoL Series Overlay - Local Relay Server
Run this before opening controller.html or going live.
Requires Python 3 (pre-installed on Windows 10/11).
"""

import json, ssl, urllib.request, threading, os
from http.server import BaseHTTPRequestHandler, HTTPServer

# =====================================================================
#  CONFIGURATION — edit these
# =====================================================================

RIOT_API_KEY = 'RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'   # <-- paste your new key here

# Your region:
#   Platform (summoner-v4 / league-v4):  euw1 | na1 | eun1 | kr | br1 | la1 | la2 | oc1 | tr1 | ru
#   Routing  (account-v1):               europe | americas | asia | esports

# =====================================================================

state = {}

POSITION_ORDER = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
POSITION_LABEL = {'TOP': 'Top', 'JUNGLE': 'Jungle', 'MIDDLE': 'Mid', 'BOTTOM': 'Bot', 'UTILITY': 'Support'}

# ── HTTP helpers ─────────────────────────────────────────────────────

def live_get(path):
    """Call the League Live Client API (localhost, self-signed cert)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    req = urllib.request.urlopen(f'https://127.0.0.1:2999{path}', context=ctx, timeout=3)
    return json.loads(req.read().decode('utf-8'))

# ── Champion / player fetch ───────────────────────────────────────────

def fetch_champions():
    """Return all 10 players sorted by team + role, with rank data."""
    try:
        players = live_get('/liveclientdata/playerlist')
    except Exception as e:
        return {'ok': False, 'error': f'Live Client unavailable ({type(e).__name__})'}

    blue = [p for p in players if p.get('team') == 'ORDER']
    red  = [p for p in players if p.get('team') == 'CHAOS']

    def sort_key(p):
        pos = p.get('position', '').upper()
        return POSITION_ORDER.index(pos) if pos in POSITION_ORDER else 99

    blue.sort(key=sort_key)
    red.sort(key=sort_key)

    result = []
    for p in blue + red:
        pos = p.get('position', '').upper()
        result.append({
            'championName': p.get('championName', ''),
            'summonerName': p.get('summonerName', ''),
            'team':         p.get('team', ''),
            'position':     POSITION_LABEL.get(pos, pos.capitalize()),
            'runes':        p.get('runes', {}),
        })

    return {'ok': True, 'players': result}


# ── In-game stats fetch ────────────────────────────────────────────────

def fetch_stats():
    """Return live in-game stats for all 10 players, sorted by team+role."""
    try:
        alldata = live_get('/liveclientdata/allgamedata')
    except Exception as e:
        return {'ok': False, 'error': f'Live Client unavailable ({type(e).__name__})'}

    players   = alldata.get('allPlayers', [])
    game_time = alldata.get('gameData', {}).get('gameTime', 1)
    events    = alldata.get('events', {}).get('Events', [])

    # Sum kills per team directly from scores (more reliable than event log)
    team_kills = {'ORDER': 0, 'CHAOS': 0}
    for p in players:
        team = p.get('team', '')
        if team in team_kills:
            team_kills[team] += p.get('scores', {}).get('kills', 0)

    def sort_key(p):
        pos = p.get('position', '').upper()
        return POSITION_ORDER.index(pos) if pos in POSITION_ORDER else 99

    blue = sorted([p for p in players if p.get('team') == 'ORDER'], key=sort_key)
    red  = sorted([p for p in players if p.get('team') == 'CHAOS'],  key=sort_key)

    mins = max(game_time / 60, 0.1)

    result = []
    for p in blue + red:
        pos    = p.get('position', '').upper()
        scores = p.get('scores', {})
        items  = p.get('items',  [])
        team   = p.get('team', 'ORDER')

        k  = scores.get('kills',       0)
        d  = scores.get('deaths',      0)
        a  = scores.get('assists',     0)
        cs = scores.get('creepScore',  0)
        vs = scores.get('wardScore',   0)
        tk = team_kills.get(team, 0)
        kp = round((k + a) / tk * 100) if tk > 0 else 0

        # Gold = sum of item prices (excludes trinket slot 6/7 ideally, but price=0 for trinkets anyway)
        gold = sum(i.get('price', 0) for i in items)

        result.append({
            'summonerName':     p.get('summonerName', ''),
            'championName':     p.get('championName', ''),
            'team':             team,
            'position':         POSITION_LABEL.get(pos, pos.capitalize()),
            'level':            p.get('level', 1),
            'kills':            k,
            'deaths':           d,
            'assists':          a,
            'kda':              round((k + a) / max(d, 1), 2),
            'cs':               cs,
            'csPerMin':         round(cs / mins, 1),
            'killParticipation':kp,
            'visionScore':      round(vs),
            'gold':             gold,
            'items':            [{'name': i.get('displayName',''), 'id': i.get('itemID',0), 'price': i.get('price',0)}
                                 for i in sorted(items, key=lambda x: x.get('slot',9))[:6]],
            'isDead':           p.get('isDead', False),
        })

    return {'ok': True, 'players': result, 'gameTime': round(game_time)}


# ── HTTP handler ──────────────────────────────────────────────────────

# ── Combined fetch: runes + live stats ───────────────────────────────────

def fetch_full():
    """Single call returning rune + live-stats data merged per player."""
    # Run both fetches in parallel
    champ_result = [None]
    stats_result = [None]

    def do_champs(): champ_result[0] = fetch_champions()
    def do_stats():  stats_result[0]  = fetch_stats()

    t1 = threading.Thread(target=do_champs)
    t2 = threading.Thread(target=do_stats)
    t1.start(); t2.start()
    t1.join();  t2.join()

    champs = champ_result[0]
    stats  = stats_result[0]

    # If live client is not up, fall back to rune-only data
    if not champs.get('ok'):
        return champs  # propagate the error

    players = champs['players']  # has runes, summonerName, championName

    # Merge live stats if available
    if stats.get('ok') and stats.get('players'):
        stats_by_name = {p['summonerName']: p for p in stats['players']}
        for p in players:
            live = stats_by_name.get(p['summonerName'], {})
            p['kills']             = live.get('kills', None)
            p['deaths']            = live.get('deaths', None)
            p['assists']           = live.get('assists', None)
            p['cs']                = live.get('cs', None)
            p['kda']               = live.get('kda', None)
            p['level']             = live.get('level', None)
            p['visionScore']       = live.get('visionScore', None)
            p['killParticipation'] = live.get('killParticipation', None)
            p['gold']              = live.get('gold', None)
            p['isDead']            = live.get('isDead', False)
        return {'ok': True, 'players': players, 'gameTime': stats.get('gameTime', 0)}
    else:
        return {'ok': True, 'players': players, 'gameTime': 0}


class Handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.cors(204)

    def do_GET(self):
        try:
            path = self.path.split('?')[0]
            if path == '/state':
                self.cors(200)
                self.wfile.write(json.dumps(state).encode())
            elif path == '/overlay' or path == '/':
                overlay_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlay.html')
                with open(overlay_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.end_headers()
                self.wfile.write(data)
            elif path.startswith('/champions'):
                self.cors(200)
                self.wfile.write(json.dumps(fetch_champions()).encode())
            elif path.startswith('/stats'):
                self.cors(200)
                self.wfile.write(json.dumps(fetch_stats()).encode())
            elif path.startswith('/full'):
                self.cors(200)
                self.wfile.write(json.dumps(fetch_full()).encode())
            else:
                self.cors(404)
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass  # client disconnected mid-response — normal with frequent polling

    def do_POST(self):
        global state
        try:
            if self.path == '/state':
                n     = int(self.headers.get('Content-Length', 0))
                state = json.loads(self.rfile.read(n))
                self.cors(200)
                self.wfile.write(b'ok')
            else:
                self.cors(404)
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass

    def cors(self, code):
        self.send_response(code)
        self.send_header('Content-Type',  'application/json')
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.end_headers()

    def log_message(self, *a):
        pass

if __name__ == '__main__':
    PORT = 8765
    print(f"✅  Relay server running at http://localhost:{PORT}")
    print(f"    Overlay URL: http://localhost:{PORT}/overlay")
    print(f"    Keep this window open while streaming.")
    print(f"    Press Ctrl+C to stop.\n")
    HTTPServer(('localhost', PORT), Handler).serve_forever()
