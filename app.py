# version information
version = '0.0.0.1'
update_date = '2025/07/18'

from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import psutil
from list.list_html_dynamic import *
import threading
import os
import datetime
import pyautogui
import tkinter as tk

app = Flask(__name__)

# グローバル変数を使用してカメラの状態を管理
camera = None
result = ""

def show_tkinter_window():
    global result
    def on_ok():
        global result
        result = "OK"
        root.destroy()  # ウィンドウを閉じる
    def on_ng():
        global result
        result = "NG"
        root.destroy()  # ウィンドウを閉じる
    root = tk.Tk()
    root.title("Select Action")
    tk.Label(root, text="Choose OK or NG").pack(pady=10)
    tk.Button(root, text="OK", command=on_ok).pack(side=tk.LEFT, padx=20, pady=20)
    tk.Button(root, text="NG", command=on_ng).pack(side=tk.RIGHT, padx=20, pady=20)
    root.mainloop()

def init_camera():
    global camera
    if camera is not None:
        camera.release()  # 既存のカメラをリリース
    camera = cv2.VideoCapture(0)  # カメラを初期化

def generate_frames():
    while True:
        if camera is None or not camera.isOpened():
            init_camera()  # カメラが開いていない場合は初期化

        success, frame = camera.read()  # カメラからフレームを取得
        if not success:
            init_camera()
            time.sleep(5)  # 取得に失敗した場合は1秒待つ
            continue  # 次のループへ

        # フレームをJPEG形式にエンコード
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()  # バイナリデータに変換

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # HTTPレスポンス形式に整形

screenshot_dir = "static/screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

@app.route('/')
@app.route('/home')
@app.route('/main')

@app.route('/system')
def html_system():
    return render_template(
        'system.html',
        version = version)

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    message = None
    if request.method == 'POST':
        message = request.form.get('message')
        print("Received message:", message)  # メッセージをコンソールに表示
        os.system(f'msg * "これは通知メッセージです。⇒　{message}　"')
    return render_template('setting.html', message=message)

@app.route('/request_action', methods=['POST'])
def request_action():
    # Tkinterウィンドウを別スレッドで実行
    threading.Thread(target=show_tkinter_window).start()
    global result
    result = "None"
    return "選択肢が表示されました。"

@app.route('/result', methods=['GET'])
def get_result():
    global result
    return f"選択された結果: {result}" if result else "まだ選択されていません。"
    
@app.route('/data')
def data():
    # Prepare data to send
    data = {
        'html_dynamic_system': html_dynamic_system
    }
    return jsonify(data)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/screenshot', methods=['POST'])
def screenshot():
    # スクリーンショットを撮影
    screenshot = pyautogui.screenshot()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
    screenshot.save(screenshot_path)  # スクリーンショットを保存
    #return f"/{screenshot_path}"  # 画像のパスを返す
    #return f"/{screenshot_path.split('/')[-1]}"
    return f"/static/screenshots/{os.path.basename(screenshot_path)}"  # 画像のフルパスを返す

    print(screenshot_path)
    print(f"/static/screenshots/{os.path.basename(screenshot_path)}")

@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(screenshot_dir, filename)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def thread02_systeminfo():
    global html_dynamic_system
    while True:
        if html_dynamic_system[0] == '':
            html_dynamic_system[0] = '* ♥ *'
        else:
            html_dynamic_system[0] = ''
        try:
            html_dynamic_system[1] = f'{psutil.cpu_percent(interval=1):.2f}'
            html_dynamic_system[2] = f'{psutil.virtual_memory().percent:.2f}'
        except:
            html_dynamic_system[1] = "情報取得不可"
            html_dynamic_system[2] = "情報取得不可"
        try:
            html_dynamic_system[3] = f'{psutil.sensors_temperatures()["cpu_thermal"][0].current:.2f}'
        except:
            html_dynamic_system[3] = "情報取得不可"
        try:
            power_result = subprocess.run(['dmesg'], capture_output=True, text=True)
            power_log = power_result.stdout
            if 'Under-voltage detected!' in power_log:
                html_dynamic_system[4] = 'Warning'
            else:
                html_dynamic_system[4] = 'OK'
        except:
            html_dynamic_system[4] = "情報取得不可"
        time.sleep(1)


if __name__ == '__main__':
    init_camera()  # アプリ起動時にカメラを初期化
    thread02 = threading.Thread(target=thread02_systeminfo, daemon=True)
    time.sleep(0.5)
    thread02.start()
    app.run(host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'))
