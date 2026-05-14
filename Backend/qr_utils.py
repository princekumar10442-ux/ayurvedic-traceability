import qrcode
import json
import os

def generate_qr(block, filename):
    # Convert block to JSON string
    data = json.dumps(block, indent=2)

    # Save inside the static folder
    static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
    os.makedirs(static_dir, exist_ok=True)  # ensure folder exists
    path = os.path.join(static_dir, filename)

    # Generate and save QR
    img = qrcode.make(data)
    img.save(path)

    # Return relative path for Flask's static route
    return filename
