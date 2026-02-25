import os
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

def get_rates():
    # ۱. تعریف کانال‌ها
    URL_HERAT = "https://t.me/s/NerkhYab_Khorasan"
    URL_TEHRAN = "https://t.me/s/dollarsbze"
    FILE_NAME = 'last_rates.json'
    now = datetime.now()

    # ۲. الگوهای استخراج (Regex)
    mapping_herat = {
        "دالر هرات": r"دالر.*?(\d+[.,]\d+)",
        "یورو هرات": r"یورو.*?(\d+[.,]\d+)",
        "تومان چک": r"چک.*?(\d+[.,]\d+)",
        "تومان بانکی": r"بانکی.*?(\d+[.,]\d+)",
        "کلدار": r"کلدار.*?(\d+[.,]\d+)"
    }
    pattern_tehran = r"دلار تهران ⛳️\s*:\s*([\d,]+)"

    # ۳. لود کردن دیتای قبلی
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "rates" not in data: data = {"rates": {}}
        except: data = {"rates": {}}
    else:
        data = {"rates": {}}

    headers = {'User-Agent': 'Mozilla/5.0'}

    def update_data(key, val, is_formatted=False):
        nv = float(val)
        
        # اگر کلید وجود نداشت، ایجاد شود
        if key not in data["rates"]:
            data["rates"][key] = {"history": [nv], "status": "up", "percent": "0.00%"}
        
        # --- اصلاح اصلی: حذف بخش حذف دیتای صبح (now.hour == 0) ---
        # دیگر دیتای شروع روز پاک نمی‌شود تا تاریخچه بماند.

        # قیمت مبنا برای درصد تغییرات (اولین قیمت موجود در تاریخچه)
        base_price = float(data["rates"][key]["history"][0])
        
        data["rates"][key]["status"] = "up" if nv >= base_price else "down"
        diff = ((nv - base_price) / base_price * 100) if base_price != 0 else 0
        data["rates"][key]["percent"] = f"{diff:+.2f}%"
        
        data["rates"][key]["current"] = f"{int(nv):,}" if is_formatted else f"{nv:.2f}"
        
        # آپدیت تاریخچه برای نمودار (تا ۱۰۰۰ نقطه داده برای یک ماه)
        if data["rates"][key]["history"][-1] != nv:
            data["rates"][key]["history"].append(nv)
            
            # نگه داشتن ۱۰۰۰ آیتم (حدوداً دیتای یک ماه)
            if len(data["rates"][key]["history"]) > 1000:
                data["rates"][key]["history"].pop(0)

    def process_source(url, is_tehran=False):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            recent_messages = list(reversed(messages[-50:]))
            
            for msg in recent_messages:
                text = msg.get_text(separator=" ").replace('\n', ' ')
                if is_tehran:
                    match = re.search(pattern_tehran, text)
                    if match:
                        val_raw = match.group(1).replace(',', '')
                        update_data("دلار تهران", val_raw, is_formatted=True)
                        return
                else:
                    for key, pattern in mapping_herat.items():
                        if key in updated_keys: continue
                        match = re.search(pattern, text)
                        if match:
                            val = match.group(1).replace(',', '.')
                            update_data(key, val)
                            updated_keys.add(key)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    updated_keys = set()
    process_source(URL_HERAT, is_tehran=False)
    process_source(URL_TEHRAN, is_tehran=True)

    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Success! History updated at {now.strftime('%H:%M')}")

if __name__ == "__main__":
    get_rates()
