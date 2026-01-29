from flask import Flask, request, jsonify, render_template
from core import get_bot_reply
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

    # Kirim file index.html dari folder aplikasi (tidak perlu folder templates)
    return send_from_directory(str(BASE_DIR), "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "")
    reply = get_bot_reply(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    # debug=True supaya mudah melihat error saat pengembangan
    app.run(debug=True)