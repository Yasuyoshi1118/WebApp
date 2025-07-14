from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# IPカメラのストリームURLを指定
# 例: rtsp://username:password@ip_address:port/path
#IP_CAMERA_URL = "rtsp://admin:Admin12345@192.168.3.89:32014/stream2"  # ここにIPカメラのURLを入力します
#IP_CAMERA_URL = "http://192.168.3.89:554/video"  # ここにIPカメラのURLを入力します
IP_CAMERA_URL = "rtsp://239.192.0.89:37004/h264"  # ここにIPカメラのURLを入力します


#rtsp://username:password@<camera_ip>:<port>/path
#http://<camera_ip>:<port>/video

def generate_frames():
    # IPカメラの映像を取得
    cap = cv2.VideoCapture(IP_CAMERA_URL)
    while True:
        success, frame = cap.read()  # カメラからフレームを取得
        if not success:
            break
        else:
            # フレームをJPEG形式にエンコード
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()  # バイナリデータに変換

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # HTTPレスポンス形式に整形

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, ssl_context=('cert.pem', 'key.pem'))