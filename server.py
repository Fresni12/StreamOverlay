#!/usr/bin/env python3
"""
LoL Series Overlay - Local Relay Server
Run this before opening controller.html or going live.
Requires Python 3 (pre-installed on Windows 10/11).
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

state = {}

class Handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_cors(204)

    def do_GET(self):
        if self.path == '/state':
            body = json.dumps(state).encode()
            self.send_cors(200)
            self.wfile.write(body)
        else:
            self.send_cors(404)

    def do_POST(self):
        if self.path == '/state':
            global state
            length = int(self.headers.get('Content-Length', 0))
            state  = json.loads(self.rfile.read(length))
            self.send_cors(200)
            self.wfile.write(b'ok')
        else:
            self.send_cors(404)

    def send_cors(self, code):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # Silence request logs (comment out to see them)
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    PORT = 8765
    print(f"✅  Relay server running at http://localhost:{PORT}")
    print(f"    Keep this window open while streaming.")
    print(f"    Press Ctrl+C to stop.\n")
    HTTPServer(('localhost', PORT), Handler).serve_forever()
