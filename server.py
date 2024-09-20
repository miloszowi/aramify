from http.server import BaseHTTPRequestHandler, HTTPServer
import re
from urllib.parse import urlparse, parse_qs
from jinja2 import Template
from champion_provider import ChampionProvider


class Server(BaseHTTPRequestHandler):

    def parse_path_and_params(self):
        match = re.search(r"/\w+/(\d+)", self.path)
        players = int(match.group(1)) if match else None

        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        bench = int(query_params.get('bench', [3])[0])
        champions = int(query_params.get('champions', [2])[0])
        exclude_tags = query_params.get('exclude', [])

        return players, bench, champions, exclude_tags

    def load_template(self, filename):
        with open(filename) as file_:
            return Template(file_.read())

    def render_template(self, players, bench, champions, exclude_tags):
        template = self.load_template("index.html")
        return template.render(
            champion_provider=ChampionProvider(exclude_tags),
            players=players,
            midpoint=players // 2,
            bench=bench,
            champions=champions,
            exclude_tags=exclude_tags
        )

    def send_response_with_content(self, code, content, content_type="text/html"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_GET(self):
        players, bench, champions, exclude_tags = self.parse_path_and_params()

        if not players or players > 10:
            return self.handle_bad_request()

        rendered_html = self.render_template(players, bench, champions, exclude_tags)
        self.send_response_with_content(200, rendered_html)

    def handle_bad_request(self):
        error_content = self.load_template('400.html').render()
        self.send_response_with_content(400, error_content)


def run(server_class=HTTPServer, handler_class=Server, port=8111):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
