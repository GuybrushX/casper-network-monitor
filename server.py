from flask import Flask, send_file

app = Flask(__name__)


@app.route('/')
def get_image():
    return send_file("data/graph_latest.png", mimetype='image/png')


@app.route('/ips')
def ips():
    return send_file("data/ips_latest.csv", mimetype='text/text')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
