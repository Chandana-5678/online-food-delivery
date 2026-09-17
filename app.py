import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

def response():
    return {'application': 'Jenkins CI/CD Lab', 'commit': os.environ.get('APP_COMMIT', 'development'),
            'version': open('/app/version.txt').read().strip() if os.path.exists('/app/version.txt') else 'v1'}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(response()).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8081), Handler).serve_forever()
