import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000").rstrip("/")


class EventManagerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/api/"):
            return super().do_GET()

        upstream_path = self.path[len("/api") :]
        request = Request(
            f"{BACKEND_URL}{upstream_path}",
            headers={"Accept": self.headers.get("Accept", "*/*")},
        )

        try:
            with urlopen(request, timeout=10) as response:
                body = response.read()
                status = response.status
                content_type = response.headers.get("Content-Type", "application/json")
        except HTTPError as error:
            body = error.read()
            status = error.code
            content_type = error.headers.get("Content-Type", "application/json")
        except URLError as error:
            self.log_error("Backend request failed: %s", error)
            body = b'{"detail":"Backend service is unavailable"}'
            status = 502
            content_type = "application/json"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 80), EventManagerHandler).serve_forever()
