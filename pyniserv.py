#pyniserv.py

import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

class SimpleHandler(BaseHTTPRequestHandler):
    def _serve_file(self, file_path: str) -> None:
        """
        Send the contents of *file_path* with an appropriate MIME type.

        If the file is missing, a 404 error is sent instead.
        """
        try:
            with open(file_path, "rb") as fh:
                content = fh.read()
        except FileNotFoundError:
            self.send_error(404, f"File not found: {file_path}")
            return

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        # Build response -------------------------------------------------
        self.send_response(200)
        self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()

        try:
            self.wfile.write(content)
        except BrokenPipeError:          # client closed early
            pass

    def _list_directory(self, path: str) -> None:
        short = path.split("/")
        """
        Generate a very simple HTML page that lists all files/directories in *path*.
        """
        try:
            entries = os.listdir(path)
        except OSError as exc:
            self.send_error(500, f"Could not list directory: {exc}")
            return

        # Build a minimal HTML table ------------------------------------
        rows = [
            f'<tr><td>{name}</td></tr>' for name in sorted(entries)
        ]
        html_body = (f"""
            <!DOCTYPE html>
            <html lang='en'><head>
            <meta charset='utf-8'>
            <title>Directory listing</title>
            </head><body>
            <h1>Listing of {short[len(short) - 1]}</h1>
            <table border='1'>
            {"".join(rows)}
            </table></body></html>"""
        ).encode("utf-8")

        # Send response -------------------------------------------------
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_body)))
        self.end_headers()
        try:
            self.wfile.write(html_body)
        except BrokenPipeError:
            pass

    
    def do_GET(self) -> None:
        if self.path in ["/bootdev"]:
            self.send_response(200)
            print(f"Serving...{self.path}")
            file_path = "bootdev.html"
            try:
                with open(file_path, "rb") as fh:
                    content = fh.read()
            except FileNotFoundError:          # graceful 404 if the file disappears
                self.send_error(404, f"File not found: {file_path}")
                return
            # Guess MIME type – for .html this will be 'text/html'
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"
            #print(mime_type)
            self.send_header("Content-Type", mime_type)
            self.send_header("charset", "utf-8")
            #print(content)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            try:
                self.wfile.write(content)
            except BrokenPipeError:
                pass
            return

        if self.path == "/":
            cwd = os.getcwd()           # serve from *current* working directory
            print(f"Listing directory: {cwd}")
            self._list_directory(cwd)
            return

        # --- 3️⃣  /files/<name> (serve a specific file) -----------------
        if self.path.startswith("/"):
            # decode %-encoding (e.g. space -> %20), then strip the prefix
            rel_path = unquote(self.path[1:])   # "/files/" is 7 chars long

            # Prevent directory traversal attacks:
            safe_path = os.path.normpath(os.path.join(os.getcwd(), rel_path))

            if not safe_path.startswith(os.getcwd()):
                self.send_error(403, "Forbidden")
                return

            print(f"Serving file: {safe_path}")
            self._serve_file(safe_path)
            return

        self.send_error(404, f"Page not found: {self.path}")

def dummy_srv(server_class=HTTPServer, handler_class=SimpleHandler):
    server_address = ('127.0.0.1', 8080)
    httpd = server_class(server_address, handler_class)
    #handler_class.handle
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:          # Ctrl‑C
        print("\nShutting down.")
        httpd.server_close()

def main():
    dummy_srv()

if __name__ == "__main__":
    main()