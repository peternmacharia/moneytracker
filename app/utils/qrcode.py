"""
app/utils/qr.py - Turns a TOTP URI into a base64 PNG for use in an <img> tag.
"""

import base64
import io
import qrcode


def generate_qr_b64(uri: str) -> str:
    """
    Render a QR code for the given URI and return it as a base64 PNG string.
    """
    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# End of file: app/utils/qr.py
