from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask YouTube Comment Analyzer is Running!"

if __name__ == '__main__':
    app.run(debug=True)
