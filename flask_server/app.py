from flask import Flask, send_from_directory

STATIC_FOLDER = "../web_client"

app = Flask(__name__, static_url_path='', static_folder=STATIC_FOLDER)

@app.route('/')
def hello_world():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
