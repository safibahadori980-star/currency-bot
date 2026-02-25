import requests
import re
import json
import os
from datetime import datetime

# منابع دیتای ما
CHANNEL_HERAT = "https://t.me/s/NerkhYab_Khorasan"
CHANNEL_TEHRAN = "https://t.me/s/dollarsbze"

def clean_html(raw):
    return re.sub(r'<.*?>', '', raw)

def get_messages(url):
    try:
        res = requests.get(url, timeout=20)
        messages = re.findall(r'<div class="tgme_widget_message_text.*?>(.*?)</div>', res.text, re.S)
        return [clean_html(m) for m in messages[-30:]]
    except:
        return []

def load_old():
    if os.path.exists("last_rates.json"):
        with open("last_rates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"rates": {}}

def get_rates():
    # ۱. دریافت پیام‌ها از هر دو کانال
    messages_herat = get_messages(CHANNEL_HERAT)
    messages_tehran = get_messages(CHANNEL_TEHRAN)
    
    # ۲. لیست ارزهای هرات (منبع اول)
    found_prices = {
        "دالر هرات": "63.20",
        "یورو هرات": "73.20",
        "تومان چک": "0.47",
        "تومان بانکی": "0.38",
        "کلدار": "214.00"
    }

    # استخراج دیتای هرات
    for msg in reversed(messages_herat):
        for key in found_prices.keys():
            search_key = key.split()[0] 
            if search_key in msg:
                # همان منطق قبلی شما برای هرات
                pattern = rf"{search_key}.*?(\d+[.,]\d+)"
                match = re.search(pattern, msg)
                if match:
                    found_prices[key] = match.group(1).replace(',', '.')

    # ۳. استخراج اختصاصی دلار تهران (منبع دوم)
    tehran_price = "---"
    #Regex اختصاصی برای مدل: دلار تهران ⛳️ : 165,920
    tehran_pattern = r"دلار تهران ⛳️\s*:\s*([\d,]+)"
    
    for msg in reversed(messages_tehran):
        match = re.search(tehran_pattern, msg)
        if match:
            # حذف کاما برای تبدیل به عدد (مثل 165,920 -> 165920)
            tehran_price = match.group(1).replace(',', '')
            break
    
    # اضافه کردن تهران به لیست نهایی
    if tehran_price != "---":
        found_prices["دلار تهران"] = tehran_price

    old_data = load_old()
    new_rates = {}

    for key, current_price in found_prices.items():
        if current_price == "---": continue
        
        old_val = old_data.get("rates", {}).get(key, {}).get("current", "0")
        
        # تبدیل به عدد برای محاسبات
        nv = float(current_price.replace(',', ''))
        ov = float(str(old_val).replace(',', '')) if old_val != "---" else nv
        
        status = "up" if nv > ov else ("down" if nv < ov else "same")
        
        percent = "0.00%"
        if ov != 0:
            diff = ((nv - ov) / ov) * 100
            percent = f"{diff:+.2f}%"

        history = old_data.get("rates", {}).get(key, {}).get("history", [])
        if not history or history[-1] != nv:
            history.append(nv)
            if len(history) > 20: history.pop(0)

        # فرمت نمایش برای تهران (با کاما) و بقیه (ساده)
        display_price = f"{int(nv):,}" if key == "دلار تهران" else current_price

        new_rates[key] = {
            "current": display_price,
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
