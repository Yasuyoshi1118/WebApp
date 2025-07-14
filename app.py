from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    name = 'Guest'
    if request.method == 'POST':
        name = request.form.get('name', 'Guest')
    return render_template('index.html', name=name)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)#host設定により外部からアクセス可能になる
