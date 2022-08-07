# Simple http bs
from wsgiref.simple_server import make_server
import threading


def hello_world_app(_, start_response):
    status = '200 OK'  # HTTP Status
    headers = [('Content-type', 'text/plain; charset=utf-8')]  # HTTP Headers
    start_response(status, headers)

    # The returned object is going to be printed
    return [b"Hello World"]


def main():
    with make_server('127.0.0.1', 8000, hello_world_app) as httpd:
        print("Serving on port 8000...")

        # Serve until process is killed
        httpd.serve_forever()


def start():
    thread = threading.Thread(target=main, name="HTTP_SERV")
    thread.setDaemon(True)
    thread.start()
