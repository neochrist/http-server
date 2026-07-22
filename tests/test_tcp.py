import pytest
import socket
import threading
import os

from http_server.tcp import Server

host = "localhost"
port = 65432


def test_tcp_construct():
    server = Server(host=host, port=port)
    assert server.host == host
    assert server.port == port


def test_tcp_start():

    server = Server(host=host, port=port)
    server.start()

    assert server.running

    with pytest.raises(RuntimeError):
        server.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.close()

    server.stop()
    assert server.running is False

    server2 = Server(host=host, port=port)
    server2.start()  # woudl raise OSError without SO_REUSEADDR
    server2.stop()


def test_tcp_serve():
    server = Server(host=host, port=port)

    with pytest.raises(RuntimeError):
        server.serve()

    server.start()

    thread = threading.Thread(target=server.serve, daemon=True)
    thread.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.sendall(b"hello")
    response = client.recv(1024)
    client.close()

    server.stop()

    thread.join(timeout=2)

    assert response == b"hello"


def test_tcp_serve__sequential_clients():
    server = Server(host=host, port=port)
    server.start()

    thread = threading.Thread(target=server.serve, daemon=True)
    thread.start()

    # client1
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect((host, port))
    client1.sendall(b"first")
    response1 = client1.recv(1024)
    client1.close()

    # client2
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2.connect((host, port))
    client2.sendall(b"second")
    response2 = client2.recv(1024)
    client2.close()

    server.stop()

    assert response1 == b"first"
    assert response2 == b"second"


def test_tcp_serve__minimal_interaction():
    server = Server(host=host, port=port)
    server.start()

    thread = threading.Thread(target=server.serve, daemon=True)
    thread.start()

    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect((host, port))
    client1.close()

    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2.connect((host, port))
    client2.sendall(b"client2")
    response2 = client2.recv(1024)
    client2.close()

    server.stop()

    assert response2 == b"client2"


def test_tcp_handle_connection():
    server = Server(host=host, port=port)
    server_side, client_side = socket.socketpair()

    client_side.sendall(b"hello")
    client_side.shutdown(socket.SHUT_WR)

    server.handle_connection(server_side)

    response = client_side.recv(1024)

    server_side.close()
    client_side.close()
    assert response == b"hello"


def test_tcp_handle_connection__large_payload():
    server = Server(host=host, port=port)
    server_side, client_side = socket.socketpair()

    # generates 10,000 bytes
    payload = os.urandom(10_00)
    client_side.sendall(payload)

    # closes only sending, still can recieve
    client_side.shutdown(socket.SHUT_WR)

    server.handle_connection(server_side)
    server_side.close()

    recieved = b""
    while True:
        chunk = client_side.recv(4096)
        if not chunk:
            break
        recieved += chunk

    client_side.close()
    server.stop()

    assert recieved == payload


def test_tcp_stop():
    server = Server(host=host, port=port)

    assert server.running is False
    assert server.sock is None

    server.start()
    sock_ref = server.sock
    server.stop()

    assert server.running is False
    assert server.sock is None
    assert sock_ref is not None

    with pytest.raises(OSError):
        sock_ref.send(b"test")
