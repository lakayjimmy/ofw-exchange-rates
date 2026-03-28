import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import pytz

# --- CONFIG ---
API_KEY = os.environ["EXCHANGE_API_KEY"]
FOLDER_ID = os.environ["GDRIVE_FOLDER_ID"]
CREDS_JSON = os.environ["GDRIVE_CREDENTIALS"]

# --- FETCH RATES ---
url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/PHP"
response = requests.get(url)
data = response.json()
rates = data["conversion_rates"]

currencies = {
    "USD": ("🇺🇸", "US Dollar"),
    "EUR": ("🇪🇺", "Euro"),
    "JPY": ("🇯🇵", "Japanese Yen"),
    "AED": ("🇦🇪", "UAE Dirham"),
    "SAR": ("🇸🇦", "Saudi Riyal"),
    "HKD": ("🇭🇰", "Hong Kong Dollar"),
}

# --- IMAGE SETTINGS ---
W, H = 1080, 1080
bg_color = (18, 18, 28)
gold = (212, 175, 55)
white = (255, 255, 255)
gray = (160, 160, 180)
line_color = (40, 40, 60)

img = Image.new("RGB", (W, H), bg_color)
draw = ImageDraw.Draw(img)

# --- FONTS (default fallback) ---
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    font_rate = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
except:
    font_title = font_sub = font_label = font_rate = font_small = ImageFont.load_default()

# --- HEADER ---
draw.rectangle([0, 0, W, 130], fill=(10, 10, 20))
draw.text((W//2, 40), "OFW Business", font=font_title, fill=gold, anchor="mm")
draw.text((W//2, 95), "Daily PHP Exchange Rate", font=font_sub, fill=white, anchor="mm")

# --- GOLD LINE ---
draw.rectangle([40, 135, W-40, 138], fill=gold)

# --- DATE ---
tz = pytz.timezone("Asia/Dubai")
now = datetime.now(tz)
date_str = now.strftime("%B %d, %Y  |  %I:%M %p (Dubai Time)")
draw.text((W//2, 158), date_str, font=font_small, fill=gray, anchor="mm")

# --- RATES ---
y = 195
row_h = 120
for i, (code, (flag, name)) in enumerate(currencies.items()):
    row_bg = (22, 22, 35) if i % 2 == 0 else (28, 28, 42)
    draw.rectangle([40, y, W-40, y+row_h-8], fill=row_bg, outline=line_color, width=1)

    # Flag + Currency
    draw.text((80, y + row_h//2 - 10), flag, font=font_label, fill=white, anchor="lm")
    draw.text((150, y + row_h//2 - 18), code, font=font_label, fill=gold, anchor="lm")
    draw.text((150, y + row_h//2 + 14), name, font=font_small, fill=gray, anchor="lm")

    # Rate
    rate_val = rates.get(code, 0)
    if rate_val and rate_val != 0:
        php_per_unit = 1 / rate_val
        rate_text = f"₱ {php_per_unit:,.4f}"
    else:
        rate_text = "N/A"

    draw.text((W-80, y + row_h//2), rate_text, font=font_rate, fill=white, anchor="rm")

    y += row_h

# --- FOOTER ---
draw.rectangle([0, H-70, W, H], fill=(10, 10, 20))
draw.rectangle([40, H-68, W-40, H-65], fill=gold)
draw.text((W//2, H-35), "Follow OFW Business for daily updates", font=font_small, fill=gray, anchor="mm")

# --- SAVE IMAGE ---
filename = f"php_rates_{now.strftime('%Y%m%d')}.png"
img.save(filename)

# --- UPLOAD TO GOOGLE DRIVE ---
creds_dict = json.loads(CREDS_JSON)
creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive"])
service = build("drive", "v3", credentials=creds)

file_metadata = {"name": filename, "parents": [FOLDER_ID]}
media = MediaFileUpload(filename, mimetype="image/png")
service.files().create(body=file_metadata, media_body=media, fields="id").execute()

print(f"✅ Done! {filename} uploaded to Google Drive.")
