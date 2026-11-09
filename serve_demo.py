"""Local browser demo. Opens no windows and does not control the desktop."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import sys
import threading
from urllib.parse import urlparse
from demo import Engine, SCENES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=7867)
    ap.add_argument('--work', type=Path)
    args = ap.parse_args()
    if sys.version_info[:2] != (3, 9):
        raise SystemExit('Use Python 3.9 with requirements.txt installed.')
    engine = Engine(args.work)
    state = {'status': 'preparing', 'scenes': list(SCENES)}
    lock = threading.Lock()

    def prepare():
        try:
            engine.prepare()
            state['status'] = 'ready'
        except Exception as exc:
            state.update(status='error', error=str(exc))

    class Handler(BaseHTTPRequestHandler):
        def respond(self, code, data, content_type='application/json; charset=utf-8'):
            payload = json.dumps(data).encode() if isinstance(data, dict) else data
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == '/api/status':
                return self.respond(200, dict(state))
            if path in ('/', '/index.html'):
                return self.respond(200, (Path(__file__).parent/'demo/index.html').read_bytes(), 'text/html; charset=utf-8')
            if path == '/favicon.ico':
                return self.respond(204, b'')
            self.respond(404, {'error': 'Not found'})

        def do_POST(self):
            if self.path != '/api/run':
                return self.respond(404, {'error': 'Not found'})
            if state['status'] != 'ready':
                return self.respond(503, {'error': 'Source trees are not ready.'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length < 1024:
                    raise ValueError('Invalid request length')
                scene = json.loads(self.rfile.read(length)).get('scenario')
                if scene not in SCENES:
                    raise ValueError('Unknown scene')
            except (ValueError, AttributeError):
                return self.respond(400, {'error': 'Choose one of the provided scenes.'})
            try:
                with lock:
                    record = engine.run(scene)
                self.respond(200, record)
            except Exception as exc:
                self.respond(500, {'error': str(exc)})

        def log_message(self, fmt, *args):
            print(fmt % args, flush=True)

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    threading.Thread(target=prepare, daemon=True).start()
    print('Local demo: http://127.0.0.1:%d (no browser opened)' % server.server_port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
