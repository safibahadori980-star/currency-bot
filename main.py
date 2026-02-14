import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
import pytz

# نام فایل برای ذخیره نرخ‌ها
DB_FILE = "last_rates.json"

def load_last_rates():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "rates": {"دالر هرات": "63.50", "تومان بانکی": "0.39", "یورو هرات": "73.70", "کلدار (پاکستان)": "216.50", "تومان چک": "0.51"},
        "last_update": "---"
    }

def save_rates(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_latest_rate(messages, keyword, old_value):
    for msg in reversed(messages):
        if keyword in msg:
            match = re.search(r"(\d+\.\d+|\d+)", msg.split(keyword)[1])
            if match:
                return match.group(1), True
    return old_value, False

def start():
    url = "https://t.me/s/NerkhYab_Khorasan"
    current_data = load_last_rates()
    rates = current_data["rates"]
    any_new_rate = False

    try:
        res = requests.get(url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_msgs = [m.get_text() for m in soup.find_all('div', class_='tgme_widget_message_text')]
        recent_msgs = all_msgs[-30:]

        keywords = {
            "دالر هرات": "دالر به افغانی",
            "تومان بانکی": "تومان بانکی",
            "یورو هرات": "یورو به افغانی",
            "کلدار (پاکستان)": "کلدار افغانی",
            "تومان چک": "تومان چک"
        }

        for key, tg_key in keywords.items():
            new_val, found = get_latest_rate(recent_msgs, tg_key, rates[key])
            if found and new_val != rates[key]:
                rates[key] = new_val
                any_new_rate = True

        if any_new_rate:
            tz_kabul = pytz.timezone('Asia/Kabul')
            current_data["last_update"] = datetime.now(tz_kabul).strftime("%Y-%m-%d %H:%M")

        current_data["rates"] = rates
        save_rates(current_data)
        print("بروزرسانی با موفقیت انجام شد.")

    except Exception as e:
        print(f"خطا: {e}")

if __name__ == "__main__":
    start()
