from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from run_yolo1 import redact_pdf

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
REDACTED_FOLDER = 'redacted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REDACTED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save uploaded file
    original_filename = file.filename.replace(' ', '_')
    uploaded_path = os.path.join(UPLOAD_FOLDER, original_filename)
    file.save(uploaded_path)

    # Define redacted file path
    redacted_filename = f"redacted_{original_filename}"
    redacted_path = os.path.join(REDACTED_FOLDER, redacted_filename)

    # Perform redaction using YOLO
    try:
        redact_pdf(uploaded_path, redacted_path)
    except Exception as e:
        return jsonify({"error": f"Redaction failed: {str(e)}"}), 500

    return jsonify({
        "message": f"Redacted PDF saved to {redacted_path}",
        "download_url": f"http://localhost:5000/download/{redacted_filename}"
    })

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(REDACTED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
