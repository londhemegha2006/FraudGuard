
import re
from urllib.parse import urlparse


# Common result format
def result(status, reasons, next_steps, explanation=None):
    return {
        "status": status,
        "reasons": reasons,
        "next_steps": next_steps,
        "explanation": explanation or ""
    }


# 1. Email Analysis
def analyze_email(subject, sender, message):
    text = f"{subject} {sender} {message}".lower()
    reasons = []

    suspicious_words = [
        "urgent", "verify your account", "password",
        "click here", "free prize", "winner",
        "bank details", "otp", "claim now"
    ]

    for word in suspicious_words:
        if word in text:
            reasons.append(f"Suspicious wording found: {word}")

    if sender and not re.search(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", sender):
        reasons.append("Sender email address has an unusual format.")

    if not reasons:
        reasons.append("No common suspicious keywords or obvious sender-format issues were detected.")

    return result(
        "Needs Manual Verification",
        reasons,
        [
            "Verify the sender through its official website or contact number.",
            "Never share passwords, OTPs, or banking details.",
            "Avoid opening unexpected attachments or links."
        ],
        "This is a basic keyword-based email screening tool. It cannot confirm whether an email is genuine."
    )


# 2. URL Analysis
def analyze_url(raw_url):
    reasons = []

    url = raw_url.strip()

    if not url:
        return result(
            "Unable to Verify",
            ["No URL was provided."],
            ["Enter a website address."]
        )

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        domain = parsed.hostname

        if not domain or "." not in domain:
            raise ValueError("Invalid URL")

        if parsed.scheme == "http":
            reasons.append("The URL uses HTTP instead of HTTPS.")

        if "@" in url:
            reasons.append("The URL contains an @ symbol, which can hide the actual destination.")

        if re.search(r"\d+\.\d+\.\d+\.\d+", domain):
            reasons.append("The website uses an IP address instead of a normal domain name.")

        suspicious_words = [
            "login", "verify", "free", "prize",
            "secure", "update", "account", "claim"
        ]

        for word in suspicious_words:
            if word in domain.lower():
                reasons.append(f"Potentially suspicious word in domain: {word}")

        if len(domain) > 50:
            reasons.append("The domain name is unusually long.")

        if not reasons:
            reasons.append("No obvious URL warning signs were detected.")

        return result(
            "Needs Manual Verification",
            reasons,
            [
                "Check the domain spelling carefully.",
                "Visit the official website by typing its address yourself.",
                "Do not enter passwords or payment details on an unverified site."
            ],
            "This tool checks basic URL patterns. It does not check live malware databases or guarantee website safety."
        )

    except Exception:
        return result(
            "Unable to Verify",
            ["The entered URL is not in a valid format."],
            ["Enter a valid website address."]
        )


# 3. Shopping Price Analysis
def analyze_price(name, displayed, reference):
    reasons = []

    try:
        displayed = float(displayed)
        reference = float(reference)

        if displayed < 0 or reference <= 0:
            raise ValueError()

        if displayed == 0:
            reasons.append("The displayed price is zero. Verify the offer carefully.")

        elif displayed < reference * 0.3:
            reasons.append("The displayed price is much lower than the reference price.")

        elif displayed < reference * 0.7:
            reasons.append("The displayed price is considerably lower than the reference price.")

        else:
            reasons.append("No unusually large price difference was detected.")

        return result(
            "Needs Manual Verification",
            reasons,
            [
                "Compare the price on the official seller website.",
                "Check seller ratings and customer reviews.",
                "Read the return and refund policy before purchasing."
            ],
            f"Basic price comparison for {name or 'the product'}. A low price alone does not prove fraud."
        )

    except (ValueError, TypeError):
        return result(
            "Unable to Verify",
            ["Please enter valid positive numeric prices."],
            ["Check the displayed price and reference price."]
        )


# 4. Image Analysis
def analyze_image(payload, ext):
    try:
        from PIL import Image, ImageStat
        from io import BytesIO

        img = Image.open(BytesIO(payload))
        img.verify()

        img = Image.open(BytesIO(payload))
        img.load()

        width, height = img.size
        image_format = img.format or ext.upper()

        reasons = [
            f"The image is readable and uses {image_format} format.",
            f"Image dimensions: {width} x {height} pixels."
        ]

        metadata = img.info or {}

        if metadata:
            reasons.append(
                "Metadata is present. It does not prove authenticity."
            )
        else:
            reasons.append(
                "No common embedded metadata was found."
            )

        rgb_image = img.convert("RGB")
        stats = ImageStat.Stat(rgb_image)

        brightness = sum(stats.mean) / 3
        variation = sum(stats.stddev) / 3

        reasons.append(f"Average brightness: {brightness:.1f}/255.")
        reasons.append(f"Average channel variation: {variation:.1f}.")

        if width < 100 or height < 100:
            reasons.append("The image has low pixel dimensions.")
        else:
            reasons.append("The image has sufficient dimensions for basic inspection.")

        return result(
            "Unable to Verify",
            reasons,
            [
                "Compare the image with a trusted original source.",
                "Check the image source and context.",
                "Use specialist image-forensics tools if manipulation is suspected."
            ],
            "This demo checks file integrity, dimensions, metadata, and basic image statistics. It cannot reliably detect AI-generated or manipulated images."
        )

    except Exception:
        return result(
            "Unable to Verify",
            ["The uploaded file could not be decoded as a valid image."],
            ["Upload a valid JPG, JPEG, or PNG image."],
            "The image could not be analyzed."
        )


# 5. Certificate Analysis
def analyze_certificate(payload, ext, cert_id, issuer, verification_url):
    reasons = []

    if not payload:
        reasons.append("No certificate file was uploaded.")

    if not cert_id or not cert_id.strip():
        reasons.append("Certificate ID was not provided.")

    if not issuer or not issuer.strip():
        reasons.append("Certificate issuer was not provided.")

    if not verification_url or not verification_url.strip():
        reasons.append("Official verification URL was not provided.")

    if verification_url:
        try:
            parsed = urlparse(verification_url)

            if parsed.scheme not in ("http", "https") or not parsed.hostname:
                reasons.append("Verification URL format appears invalid.")

        except Exception:
            reasons.append("Could not validate the verification URL format.")

    if not reasons:
        reasons.append("Certificate details were provided, but authenticity has not been confirmed.")

    return result(
        "Unable to Verify",
        reasons,
        [
            "Contact the issuing organization using its official contact details.",
            "Verify the certificate ID on the issuer's official website.",
            "Do not rely only on the uploaded image or document."
        ],
        "This demo checks whether basic certificate details are supplied. It does not authenticate certificates or contact issuing organizations."
    )
