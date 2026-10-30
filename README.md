# FraudGuard – Digital Fraud Awareness & Detection Portal

A Flask-based educational prototype with five screening tools: email, URL, image, shopping price, and certificate.

## Features
- Responsive cybersecurity-themed interface.
- Heuristic email and URL checks.
- User-entered price comparison.
- Basic image readability/metadata inspection using Pillow.
- Optional PDF text extraction using PyMuPDF.
- File uploads are processed in memory and are not saved.
- Report form validates a report locally; it does not send it to an external authority.

## Important limitations
This is a student demo, not a professional fraud-verification service. Results are not proof of fraud or authenticity. It has no live URL reputation, marketplace price, AI-image-forensics, OCR, or official certificate database integration. Never use it as the sole basis for a high-stakes decision.

## Run on Windows PowerShell
```powershell
cd path\to\FraudGuard
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

If PowerShell blocks activation, run without activating:
```powershell
py -m pip install -r requirements.txt
py app.py
```

## Security notes
- Maximum request/file size is 8 MB.
- The app does not fetch user-supplied URLs.
- Do not deploy Flask's development server or debug mode publicly.
- Before public deployment, add CSRF protection, rate limiting, production WSGI hosting, logging policy, and a privacy review.
- Configure API keys only on the server side if trusted reputation services are added.
