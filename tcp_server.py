import socket

def start_tcp_server(callback, host='127.0.0.1', port=6000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        print(f"[TCP] Listening on {host}:{port}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"[TCP] Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    msg = data.decode('utf-8')
                    print(f"[TCP] Received: {msg}")
                    callback(msg)
