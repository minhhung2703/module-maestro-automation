import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import time

# Ensure we can import from scripts/
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from select_premium_template import select_restaurant_template

PORT = 8765
SERVICE_VERSION = "2.1-multi-device-strict"

class TemplateHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean logging
        sys.stdout.write(f"[TEMPLATE-SERVICE] {args[0]} {args[1]} -> {args[2]}\n")
        sys.stdout.flush()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "version": SERVICE_VERSION,
                "pid": os.getpid(),
                "threaded": True
            }).encode("utf-8"))
            return

        if path == "/select_restaurant_template":
            version = query.get("version", ["Premium"])[0]
            device = query.get("device", [None])[0]
            print(f"[SERVICE] Received select request for version: {version}, device: {device}", flush=True)

            if version == "Free":
                # Free version should NOT use visual search for this template
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "skipped", "reason": "Free version"}).encode("utf-8"))
                return

            import importlib
            import select_premium_template
            importlib.reload(select_premium_template)
            success = select_premium_template.select_restaurant_template(serial=device, max_scrolls=20)
            if success:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            else:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "not_found"}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_service():
    # Sử dụng ThreadingHTTPServer đa luồng để hỗ trợ nhiều thiết bị gọi API cùng lúc không bị nghẽn
    server_address = ("", PORT)
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(server_address, TemplateHandler) as httpd:
        print(f"[TEMPLATE-SERVICE] Running multi-threaded HTTP daemon on port {PORT}...", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[TEMPLATE-SERVICE] Stopping daemon...", flush=True)
        finally:
            httpd.server_close()

if __name__ == "__main__":
    run_service()
