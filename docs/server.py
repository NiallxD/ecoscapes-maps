
        import http.server
        import socketserver
        import json
        import os
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/map_config.json':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    with open('map_config.json', 'rb') as f:
                        self.wfile.write(f.read())
                    return
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        if __name__ == '__main__':
            PORT = 8000
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"Serving at port {PORT}")
                httpd.serve_forever()
        