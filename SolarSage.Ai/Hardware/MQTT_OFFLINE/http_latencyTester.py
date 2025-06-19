# save as server.py
from flask import Flask
from datetime import datetime
app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
