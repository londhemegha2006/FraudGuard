from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from detector import analyze_email, analyze_url, analyze_image, analyze_price, analyze_certificate
import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB
ALLOWED_IMAGES = {"png", "jpg", "jpeg"}
ALLOWED_CERTS = {"png", "jpg", "jpeg", "pdf"}

def json_error(message, code=400):
    return jsonify({"error": message}), code

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/email")
def email_check():
    data = request.get_json(silent=True) or {}
    subject = str(data.get("subject", ""))[:300]
    sender = str(data.get("sender", ""))[:320]
    message = str(data.get("message", ""))[:12000]
    if not (subject or sender or message):
        return json_error("Enter an email subject, sender, or message.")
    return jsonify(analyze_email(subject, sender, message))

@app.post("/api/url")
def url_check():
    data = request.get_json(silent=True) or {}
    url = str(data.get("url", ""))[:2048].strip()
    if not url:
        return json_error("Enter a URL to analyze.")
    return jsonify(analyze_url(url))

@app.post("/api/price")
def price_check():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", ""))[:200]
    displayed = data.get("displayed_price", "")
    reference = data.get("reference_price", "")
    try:
        displayed = float(displayed)
        reference = float(reference)
        if displayed < 0 or reference <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return json_error("Enter a displayed price (0 or more) and a reference price greater than 0.")
    return jsonify(analyze_price(name, displayed, reference))

@app.post("/api/image")
def image_check():
    f = request.files.get("file")
    if not f or not f.filename:
        return json_error("Choose an image file.")
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED_IMAGES:
        return json_error("Upload a JPG, JPEG, or PNG image.")
    # Analyze in memory; no upload is saved to disk.
    payload = f.read(8 * 1024 * 1024 + 1)
    if len(payload) > 8 * 1024 * 1024:
        return json_error("File is too large. Maximum size is 8 MB.")
    return jsonify(analyze_image(payload, ext))

@app.post("/api/certificate")
def certificate_check():
    f = request.files.get("file")
    if not f or not f.filename:
        return json_error("Choose a certificate file.")
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED_CERTS:
        return json_error("Upload a PDF, JPG, JPEG, or PNG certificate.")
    payload = f.read(8 * 1024 * 1024 + 1)
    if len(payload) > 8 * 1024 * 1024:
        return json_error("File is too large. Maximum size is 8 MB.")
    cert_id = str(request.form.get("certificate_id", ""))[:200]
    issuer = str(request.form.get("issuer", ""))[:200]
    verification_url = str(request.form.get("verification_url", ""))[:2048]
    return jsonify(analyze_certificate(payload, ext, cert_id, issuer, verification_url))

@app.post("/api/report")
def report():
    data = request.get_json(silent=True) or {}
    category = str(data.get("category", "Other"))[:80]
    description = str(data.get("description", ""))[:2000].strip()
    if len(description) < 10:
        return json_error("Please provide at least 10 characters describing the issue.")
    # This demo does not persist reports or collect identifying data.
    return jsonify({"status": "Received locally (demo)", "message": "Your report was validated for this demonstration. It has not been sent to an external authority."})

@app.errorhandler(413)
def too_large(_error):
    return json_error("File is too large. Maximum size is 8 MB.", 413)

if __name__ == "__main__":
    app.run(debug=True)
