import requests
import re
import json
import os

CHANNEL = "https://t.me/s/NerkhYab_Khorasan"

def clean_html(raw):
    return re.sub(r'<.*?>', '', raw)

def get_last_messages():
    res = requests.get(CHANNEL)
    html = res.text
    messages = re.findall(r'<div class="tgme_widget_message_text.*?>(.*?)</div>', html, re.S)
    
    return [clean_html(m) for m in messages[:30]]

def extract_buy(text):
    m = re.search(r'خرید\s*([\d,\.]+)', text)
    return m.group(1) if m else None

def load_old():
    if os.path.exists("last_rates.json"):
        with open("last_rates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"rates": {}}

def to_float(x):
    try:
        return float(x.replace(",", ""))
    except:
        return 0

def get_rates():
    messages = get_last_messages()

    found = {
        "دالر هرات": 63,25,
        "یورو هرات": 73,50,
        "تومان چک": 0,51,
        "تومان بانکی": 0.40,
        "کلدار (پاکستان)": 213
    }

    new_rates = {}

    for msg in messages:
        if not found["دالر هرات"] and "دالر" in msg:
            val = extract_buy(msg)
            if val:
                new_rates["دالر هرات"] = val
                found["دالر هرات"] = True

        if not found["یورو هرات"] and "یورو" in msg:
            val = extract_buy(msg)
            if val:
                new_rates["یورو هرات"] = val
                found["یورو هرات"] = True

        if not found["تومان چک"] and "تومان چک" in msg:
            val = extract_buy(msg)
            if val:
                new_rates["تومان چک"] = val
                found["تومان چک"] = True

        if not found["تومان بانکی"] and "تومان بانکی" in msg:
            val = extract_buy(msg)
            if val:
                new_rates["تومان بانکی"] = val
                found["تومان بانکی"] = True

        if not found["کلدار (پاکستان)"] and "کلدار" in msg:
            val = extract_buy(msg)
            if val:
                new_rates["کلدار (پاکستان)"] = val
                found["کلدار (پاکستان)"] = True

        if all(found.values()):
            break

    old = load_old()
    result = {}

    for k in found.keys():
        v = new_rates.get(k, "---")
        old_val = old.get("rates", {}).get(k, {}).get("price", "0")

        diff = to_float(v) - to_float(old_val)

        if diff > 0:
            trend = "up"
        elif diff < 0:
            trend = "down"
        else:
            trend = "same"

        percent = 0
        if to_float(old_val) > 0:
            percent = abs(diff) / to_float(old_val) * 100

        result[k] = {
            "price": v,
            "trend": trend,
            "percent": round(percent, 2)
        }

    return result

data = {
    "rates": get_rates()
}

with open("last_rates.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
