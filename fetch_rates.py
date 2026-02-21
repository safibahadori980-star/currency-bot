import requests
import re
import json
import os

CHANNEL = "https://t.me/s/NerkhYab_Khorasan"

def clean_html(raw):
    return re.sub(r'<.*?>', '', raw)

def get_last_messages():
    try:
        res = requests.get(CHANNEL, timeout=20)
        messages = re.findall(r'<div class="tgme_widget_message_text.*?>(.*?)</div>', res.text, re.S)
        # چک کردن ۵۰ پیام آخر برای اطمینان بیشتر
        return [clean_html(m) for m in messages[-50:]]
    except:
        return []

def extract_price(text, keyword):
    # جستجوی هوشمند برای عدد بعد از کلمه کلیدی (فروش)
    pattern = rf"{keyword}.*?(\d+[.,]\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1).replace(',', '.')
    return None

def load_old():
    if os.path.exists("last_rates.json"):
        with open("last_rates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"rates": {}}

def get_rates():
    messages = get_last_messages()
    
    # مقادیر پیش‌فرض دقیقاً طبق خواسته شما
    found_prices = {
        "دالر هرات": "63.20",
        "یورو هرات": "73.20",
        "تومان چک": "0.47",
        "تومان بانکی": "0.38",
        "کلدار": "214.00"
    }

    # جستجو در پیام‌ها (از جدید به قدیم)
    for msg in reversed(messages):
        for key in found_prices.keys():
            # جستجوی کلمه کلیدی ساده شده (مثلاً فقط 'یورو' یا 'کلدار')
            search_key = key.split()[0] 
            if search_key in msg:
                price = extract_price(msg, search_key)
                if price:
                    found_prices[key] = price

    old_data = load_old()
    new_rates = {}

    for key, current_price in found_prices.items():
        old_val = old_data.get("rates", {}).get(key, {}).get("current", "0")
        
        # محاسبه وضعیت (بالا/پایین)
        nv, ov = float(current_price), float(old_val) if old_val != "---" else float(current_price)
        status = "up" if nv > ov else ("down" if nv < ov else "same")
        
        # محاسبه درصد
        percent = "0.00%"
        if ov != 0:
            diff = ((nv - ov) / ov) * 100
            percent = f"{diff:+.2f}%"

        # آپدیت تاریخچه
        history = old_data.get("rates", {}).get(key, {}).get("history", [])
        if not history or history[-1] != nv:
            history.append(nv)
            if len(history) > 20: history.pop(0)

        new_rates[key] = {
            "current": current_price,
            "status": status,
            "percent": percent,
            "history": history
        }

    return {"rates": new_rates}

if __name__ == "__main__":
    data = get_rates()
    with open("last_rates.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("بروزرسانی با موفقیت انجام شد.")
