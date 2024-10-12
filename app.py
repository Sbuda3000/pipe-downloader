from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask!"

@app.route('/data', methods=['POST'])
def get_data():
    data = request.json
    return jsonify({
        "status": "success",
        "data_received": data
    })

if __name__ == '__main__':
    app.run(debug=True)