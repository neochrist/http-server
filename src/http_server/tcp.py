from cmath import log
import socket
import logging


class Server:
    def __init__(self, host: str, port: int) -> None:
        "Constructs Server."
        self.host = host
        self.port = port
        self.sock = None
        self.running = False

    def start(self) -> None:
        "Starts server."
        if self.sock is not None:
            raise RuntimeError("Server is already started")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.sock.settimeout(1.0)
        self.running = True
        logging.info(f"Server listening on {self.host}:{self.port}")

    def serve(self) -> None:
        """Keeps serving."""
        if self.sock is None:
            raise RuntimeError("Server must be started before serving")
        while self.running:
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self.handle_connection(conn=conn)
            conn.close()

    def handle_connection(self, conn: socket.socket) -> None:
        """Handles connection."""
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
        except ConnectionResetError:
            pass
        finally:
            conn.close()

    def stop(self) -> None:
        """Stops the proccess."""
        if self.sock is not None:
            self.running = False
            self.sock.close()
            self.sock = None
