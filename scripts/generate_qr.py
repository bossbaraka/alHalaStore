import urllib.request
import urllib.parse
import os

URL = "https://alhalastore.vercel.app/"
encoded_url = urllib.parse.quote(URL, safe='')

# 1. Standard QR Code PNG (High resolution 1000x1000, theme color #463D33)
qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=1000x1000&color=46-3D-33&bgcolor=F5-F1-E8&margin=2&data={encoded_url}"

print("Downloading QR code for:", URL)
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(qr_api, headers=headers)

try:
    with urllib.request.urlopen(req) as resp:
        qr_data = resp.read()
    with open('qr-menu.png', 'wb') as f:
        f.write(qr_data)
    print(f"[SUCCESS] Updated qr-menu.png ({len(qr_data)} bytes)")
except Exception as e:
    print(f"[ERROR] Failed to fetch QR code: {e}")
