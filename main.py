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

    def process_source(url, is_tehran=False):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            recent_messages = list(reversed(messages[-50:]))
            
            for msg in recent_messages:
                text = msg.get_text(separator=" ").replace('\n', ' ')
                
                if is_tehran:
                    # استخراج مخصوص دلار تهران
                    match = re.search(pattern_tehran, text)
                    if match:
                        val_raw = match.group(1).replace(',', '') # حذف کاما برای محاسبات
                        update_data("دلار تهران", val_raw, is_formatted=True)
                        return # به محض پیدا کردن آخرین قیمت تهران خارج شو
                else:
                    # استخراج ۵ کارت هرات
                    for key, pattern in mapping_herat.items():
                        if key in updated_keys: continue
                        match = re.search(pattern, text)
                        if match:
                            val = match.group(1).replace(',', '.')
                            update_data(key, val)
                            updated_keys.add(key)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    def update_data(key, val, is_formatted=False):
        nv = float(val)
        if key not in data["rates"]:
            data["rates"][key] = {"history": [nv], "status": "up", "percent": "0.00%"}
        
        # تازه سازی تاریخچه در شروع روز
        if now.hour == 0 and now.minute < 10:
            data["rates"][key]["history"] = [nv]

        base_price = float(data["rates"][key]["history"][0])
        data["rates"][key]["status"] = "up" if nv >= base_price else "down"
        
        diff = ((nv - base_price) / base_price * 100) if base_price != 0 else 0
        data["rates"][key]["percent"] = f"{diff:+.2f}%"
        
        # ذخیره قیمت (برای تهران با جداکننده هزارگان، برای بقیه اعشاری)
        data["rates"][key]["current"] = f"{int(nv):,}" if is_formatted else f"{nv:.2f}"
        
        # آپدیت تاریخچه برای نمودار Smooth
        if data["rates"][key]["history"][-1] != nv:
            data["rates"][key]["history"].append(nv)
            if len(data["rates"][key]["history"]) > 20: data["rates"][key]["history"].pop(0)

    # ۴. اجرای عملیات استخراج
    updated_keys = set()
    process_source(URL_HERAT, is_tehran=False)
    process_source(URL_TEHRAN, is_tehran=True)

    # ۵. ذخیره نهایی
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Success! All rates updated at {now.strftime('%H:%M')}")

if __name__ == "__main__":
    get_rates()
