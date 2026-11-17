"""Servidor estático de desenvolvimento para o frontend.

Igual ao `python3 -m http.server`, mas envia `Cache-Control: no-store` em todas
as respostas. Sem esse cabeçalho o navegador guarda HTML/CSS/JS em cache por
heurística e continua exibindo versões antigas das páginas após alterações.

Uso (dentro de frontend/):
    python3 serve.py          # porta 5500
    python3 serve.py 8080     # porta customizada
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    handler = partial(NoCacheHandler, directory=str(Path(__file__).resolve().parent))
    with ThreadingHTTPServer(("", port), handler) as server:
        print(f"Frontend em http://localhost:{port}/ (sem cache)")
        server.serve_forever()


if __name__ == "__main__":
    main()
