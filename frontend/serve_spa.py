from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

BUILD_DIR = Path(__file__).resolve().parent / "build"
os.chdir(BUILD_DIR)


class SPAHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        requested = Path(self.translate_path(self.path.split("?", 1)[0]))
        if not requested.exists() or requested.is_dir():
            self.path = "/index.html"
        super().do_GET()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 3000), SPAHandler)
    print("DrishtiSetu frontend: http://127.0.0.1:3000")
    server.serve_forever()
