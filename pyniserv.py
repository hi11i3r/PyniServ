#tiny_serv.py

from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/bootdev" or self.path == "/":
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

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            try:
                self.wfile.write(content)
            except BrokenPipeError:
                pass
            #self.wfile.flush()
            #self.wfile.close()
            #fh.close()
    
        else:
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