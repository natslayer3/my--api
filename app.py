from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
	return jsonify({"Student A01571724 - nuevo mensaje"})

if __name__ == "__main__":
	app.run(threaded=True, host='0.0.0.0', port=3000)
