from flask import Flask, render_template, jsonify
from threading import Thread
from tcp_server import start_tcp_server

app = Flask(__name__)

# 最新のメッセージを保持
latest_messages = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/messages")
def get_messages():
    return jsonify(latest_messages)

# TCPサーバーから呼ばれる関数
def add_message(msg):
    print(f"[Flask] Received: {msg}")
    latest_messages.append(msg)
    # 過去100件までに制限
    if len(latest_messages) > 5:
        latest_messages.pop(0)

if __name__ == "__main__":
    # TCPサーバースレッドを起動
    tcp_thread = Thread(target=start_tcp_server, args=(add_message,))
    tcp_thread.daemon = True
    tcp_thread.start()

    # Flaskサーバー起動
    app.run(host="0.0.0.0", port=5000)
