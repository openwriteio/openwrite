# test_gemini.py
from jetforce import JetforceApplication, Request, Response, Status
from jetforce.server import GeminiServer

class TestApp(JetforceApplication):
    def __init__(self):
        super().__init__()
        self.route("")(self.root)
        print("[DEBUG] registered root route")

    def root(self, request: Request) -> Response:
        print("[DEBUG] root() triggered")
        return Response(Status.SUCCESS, "text/gemini", "Hello from root!")

if __name__ == "__main__":
    GeminiServer(
        TestApp(),
        host="0.0.0.0",
        port=1965,
        certfile="./cert.pem",
        keyfile="./key.pem",
        hostname="openwrite.io"
    ).run()

