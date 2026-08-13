#!/usr/bin/env python3
"""Local preview server for the canonical SignKit public surface.

Legacy landing and experiment paths redirect to the root landing page so local
preview behavior matches the deployed ``_redirects`` contract.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
from fnmatch import fnmatch
import os
from urllib.parse import urlsplit, urlunsplit


CANONICAL_ROUTE = "/"
LEGACY_ROUTE_PATHS = frozenset(
    {
        "/index.html",
        "/root",
        "/root/",
        "/root.html",
        "/buy",
        "/buy/",
        "/buy.html",
        "/purchase",
        "/purchase/",
        "/purchase.html",
        "/gum",
        "/gum/",
        "/gum.html",
        "/test-variants",
        "/test-variants/",
        "/test-variants.html",
        "/new",
        "/new/",
        "/web/live",
        "/web/live/",
        "/web/live/index.html",
        "/web/new_landing_page",
        "/web/new_landing_page/",
        "/web/new_landing_page/index.html",
        "/web/cloud_workspace",
        "/web/cloud_workspace/",
        "/web/cloud_workspace/index.html",
    }
)
LEGACY_ROUTE_PREFIXES = (
    "/deploy_dist/",
    "/web/archives/",
    "/web/backups/",
    "/web/concepts/",
)
LEGACY_ROUTE_PATTERNS = ("/docs/*.html",)


class CanonicalRouteHandler(SimpleHTTPRequestHandler):
    def _redirect_legacy_route(self) -> bool:
        parsed = urlsplit(self.path)
        is_html_doc = any(fnmatch(parsed.path, pattern) for pattern in LEGACY_ROUTE_PATTERNS)
        is_retained_tree = any(parsed.path.startswith(prefix) for prefix in LEGACY_ROUTE_PREFIXES)
        if parsed.path not in LEGACY_ROUTE_PATHS and not is_html_doc and not is_retained_tree:
            return False

        location = urlunsplit(("", "", CANONICAL_ROUTE, parsed.query, ""))
        self.send_response(301)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "public, max-age=300")
        self.end_headers()
        return True

    def do_GET(self):
        if self._redirect_legacy_route():
            return

        # Handle the canonical root locally while preserving static assets.
        if urlsplit(self.path).path == CANONICAL_ROUTE:
            self.path = '/index.html'
        elif not os.path.exists(urlsplit(self.path).path.lstrip('/')):
            # Unknown extensionless route: serve 404 (closer to Pages behavior)
            if '.' not in os.path.basename(urlsplit(self.path).path):
                self.path = '/404.html'

        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    PORT = 8080
    server = HTTPServer(('127.0.0.1', PORT), CanonicalRouteHandler)
    print(f'Server running at http://127.0.0.1:{PORT}/')
    print('Legacy landing and experiment routes redirect to /.')
    print('Press Ctrl+C to stop')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n👋 Server stopped')
        server.shutdown()
