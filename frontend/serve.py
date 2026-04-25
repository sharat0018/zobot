import http.server
import socketserver
import os

PORT = 5173
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Frontend server running at http://localhost:{PORT}")
    print(f"Serving files from: {DIRECTORY}")
    httpd.serve_forever()
