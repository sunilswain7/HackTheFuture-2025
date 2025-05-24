from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
REDACTED_FOLDER = 'redacted'
os.makedirs(REDACTED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    save_path = os.path.join(REDACTED_FOLDER, f"redacted_{filename.replace(' ', '_')}")
    file.save(save_path)  # Simulate redaction process

    return jsonify({
        "message": f"Redacted PDF saved to {save_path}",
        "download_url": f"http://localhost:5000/download/redacted_{filename.replace(' ', '_')}"
    })

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(REDACTED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
