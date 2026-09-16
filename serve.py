"""Local dev server that supports HTTP Range requests.

    python serve.py          # http://127.0.0.1:8099

Why this exists instead of `python -m http.server`: the stdlib server ignores the Range
header and always returns 200 with the whole file. Chrome then reports `video.seekable`
as empty and refuses to seek, so the scroll-scrub silently does nothing. The page looks
broken locally while being perfectly fine in production, because Vercel serves ranges.

Verified behaviour this restores:
  - 206 Partial Content with Content-Range for ranged requests
  - Accept-Ranges: bytes advertised on every response
"""
import http.server
import os
import re
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_head(self):
        rng = self.headers.get("Range")
        if not rng:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            size = os.path.getsize(path)
        except OSError:
            self.send_error(404)
            return None

        m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
        if not m:
            self.send_error(400, "malformed Range")
            return None

        start_s, end_s = m.groups()
        if start_s:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1
        else:
            # suffix form: bytes=-500 means the final 500 bytes
            if not end_s:
                self.send_error(400, "malformed Range")
                return None
            start, end = max(0, size - int(end_s)), size - 1

        if start >= size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return None
        end = min(end, size - 1)

        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._limit = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        limit = getattr(self, "_limit", None)
        if limit is None:
            return super().copyfile(source, outputfile)
        self._limit = None
        remaining = limit
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server(("127.0.0.1", PORT), RangeHandler) as httpd:
    print(f"serving with Range support on http://127.0.0.1:{PORT}")
    httpd.serve_forever()
