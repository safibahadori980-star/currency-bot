import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # کلمات کلیدی گسترده‌تر برای پیدا کردن یورو و کلدار
    mapping = {
        "دالر هرات": ["دالر", "دلار"],
        "یورو هرات": ["یورو"],
        "تومان چک": ["تومان چک", "چک هرات"],
        "کلدار": ["کلدار", "پاکستا"],
        "تومان بانکی": ["تومان بانکی", "حواله ایران"]
    }

    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: data = {"rates": {}}
    else: data = {"rates": {}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')

        found_keys = set()
        # بررسی ۱۰۰ پیام آخر برای اطمینان از پیدا شدن تمام ارزها
        for msg in reversed(messages[-100:]):
            text = msg.get_text(separator=" ").replace('\n', ' ').replace(',', '.')
            
            for site_key, keywords in mapping.items():
                if site_key not in found_keys and any(k in text for k in keywords):
                    # استخراج اولین عدد (قیمت خرید)
                    match = re.search(r'(\d+\.\d+|\d+)', text)
                    if match:
                        new_val = match.group(1)
                        
                        if site_key not in data["rates"]:
                            data["rates"][site_key] = {"current": "---", "status": "same", "percent": "0.00%", "history": []}
                        
                        old_val = data["rates"][site_key].get("current", "0")
                        
                        # محاسبه وضعیت صعودی/نزولی
                        try:
                            ov, nv = float(old_val), float(new_val)
                            if nv > ov: data["rates"][site_key]["status"] = "up"
                            elif nv < ov: data["rates"][site_key]["status"] = "down"
                            if ov != 0:
                                data["rates"][site_key]["percent"] = f"{((nv-ov)/ov)*100:+.2f}%"
                        except: pass

                        data["rates"][site_key]["current"] = new_val
                        
                        # بروزرسانی تاریخچه برای نمودار منحنی (ذخیره ۱۰ تغییر آخر)
                        hist = data["rates"][site_key].get("history", [])
                        if not hist or hist[-1] != float(new_val):
                            hist.append(float(new_val))
                        if len(hist) > 10: hist.pop(0)
                        data["rates"][site_key]["history"] = hist
                        
                        found_keys.add(site_key)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"با موفقیت آپدیت شد: {list(found_keys)}")

    except Exception as e: print(f"خطا در اجرا: {e}")

if __name__ == "__main__":
    get_rates()
