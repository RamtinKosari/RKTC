#!/usr/bin/env python3
"""Simple static + JSON server for the RKTC dashboard.

Run from the project root:
    python3 dashboard/server.py

Then open http://localhost:8040 in your browser.

Override the port with the RKTC_DASHBOARD_PORT environment variable.
"""

import http.server
import json
import os
import socketserver
from pathlib import Path

PORT = int(os.environ.get("RKTC_DASHBOARD_PORT", 8040))
DASHBOARD_DIR = Path(__file__).parent
PROJECT_ROOT = DASHBOARD_DIR.parent


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/messages":
            self._serve_json(PROJECT_ROOT / "category_messages.json")
        elif self.path == "/api/categories":
            self._serve_json(PROJECT_ROOT / "categories.json")
        else:
            super().do_GET()

    def _serve_json(self, path):
        if not path.exists():
            self.send_error(404, f"File not found: {path.name}")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            self.send_error(500, str(exc))

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {self.address_string()} {format % args}")


if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"RKTC dashboard serving at http://localhost:{PORT}")
        print(f"Project root: {PROJECT_ROOT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
