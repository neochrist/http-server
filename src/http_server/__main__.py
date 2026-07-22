import argparse

from http_server.tcp import Server


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the tcp echo server.")
    parser.add_argument("--host", default="localhost", help="Host to bind to.")
    parser.add_argument("--port", type=int, default=65432, help="Port to bind to.")
    args = parser.parse_args()

    server = Server(host=args.host, port=args.port)
    server.start()
    try:
        server.serve()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
