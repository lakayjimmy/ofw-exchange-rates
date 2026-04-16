import os
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz

# --- CONFIG ---
API_KEY = os.environ["EXCHANGE_API_KEY"]

# --- CHECK IF WEEKDAY ---
tz = pytz.timezone("Asia/Manila")
now = datetime.now(tz)
if now.weekday() >= 5:  # 5=Saturday, 6=Sunday
    print("⏭️ Skipping — weekend, market closed.")
    exit(0)

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

# --- FONTS (1.5x bigger) ---
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 78)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    font_rate = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
except:
    font_title = font_sub = font_label = font_rate = font_small = ImageFont.load_default()

# --- HEADER ---
draw.rectangle([0, 0, W, 160], fill=(10, 10, 20))
draw.text((W//2, 55), "OFW Business", font=font_title, fill=gold, anchor="mm")
draw.text((W//2, 125), "Daily PHP Exchange Rate", font=font_sub, fill=white, anchor="mm")

# --- GOLD LINE ---
draw.rectangle([40, 165, W-40, 169], fill=gold)

# --- DATE ---
date_str = now.strftime("%B %d, %Y  |  %I:%M %p (Philippine Time)")
draw.text((W//2, 193), date_str, font=font_small, fill=gray, anchor="mm")

# --- RATES ---
y = 220
row_h = 135
for i, (code, (flag, name)) in enumerate(currencies.items()):
    row_bg = (22, 22, 35) if i % 2 == 0 else (28, 28, 42)
    draw.rectangle([40, y, W-40, y+row_h-8], fill=row_bg, outline=line_color, width=1)

    draw.text((80, y + row_h//2 - 14), flag, font=font_label, fill=white, anchor="lm")
    draw.text((160, y + row_h//2 - 26), code, font=font_label, fill=gold, anchor="lm")
    draw.text((160, y + row_h//2 + 20), name, font=font_small, fill=gray, anchor="lm")

    rate_val = rates.get(code, 0)
    if rate_val and rate_val != 0:
        php_per_unit = 1 / rate_val
        rate_text = f"₱ {php_per_unit:,.4f}"
    else:
        rate_text = "N/A"

    draw.text((W-80, y + row_h//2), rate_text, font=font_rate, fill=white, anchor="rm")
    y += row_h

# --- FOOTER ---
draw.rectangle([0, H-80, W, H], fill=(10, 10, 20))
draw.rectangle([40, H-78, W-40, H-74], fill=gold)
draw.text((W//2, H-38), "Follow OFW Business for daily updates", font=font_small, fill=gray, anchor="mm")

# --- SAVE ---
filename = "latest_rates.png"
img.save(filename)
print(f"✅ Image saved as {filename}")
