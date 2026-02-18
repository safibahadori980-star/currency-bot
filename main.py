import os
import json
import requests
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system('pip install beautifulsoup4')
    from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'
    
    # لیست کلمات کلیدی
    mapping = {
        "دالر هرات": "دالر",
        "یورو هرات": "یورو",
        "تومان چک": "تومان چک",
        "تومان بانکی": "تومان بانکی",
        "کلدار": "کلدار"
    }

    # ۱. خواندن دیتای قبلی (برای اینکه اگر جدید نبود، قبلی بمونه)
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"rates": {}}
    else:
        data = {"rates": {}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        # ۲. بررسی دقیق ۳۰ پیام آخر
        target_messages = messages[-30:]
        found_in_this_run = set()

        for msg in reversed(target_messages):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, telegram_key in mapping.items():
                if telegram_key in text and site_key not in found_in_this_run:
                    # پیدا کردن عدد
                    match = re.search(r'(\d+[\.,]\d+|\d+)', text)
                    if match:
                        new_val = match.group(1).replace(',', '.')
                        
                        # ۳. منطق مقایسه برای فلش‌ها و رنگ‌ها
                        if site_key in data["rates"]:
                            old_val_str = data["rates"][site_key].get("current", "---")
                            if old_val_str != "---":
                                try:
                                    old_v = float(old_val_str)
                                    new_v = float(new_val)
                                    
                                    if new_v > old_v:
                                        data["rates"][site_key]["status"] = "up" # سبز
                                    elif new_v < old_v:
                                        data["rates"][site_key]["status"] = "down" # قرمز
                                    else:
                                        data["rates"][site_key]["status"] = "same" # بدون علامت
                                    
                                    # محاسبه درصد نوسان
                                    diff = new_v - old_v
                                    percent = (diff / old_v) * 100
                                    data["rates"][site_key]["percent"] = f"{percent:+.2f}%"
                                except: pass
                        else:
                            data["rates"][site_key] = {"status": "same", "percent": "0.00%"}

                        data["rates"][site_key]["current"] = new_val
                        found_in_this_run.add(site_key)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ انجام شد. تعداد آپدیت: {len(found_in_this_run)}")

    except Exception as e:
        print(f"🔥 خطا: {e}")

if __name__ == "__main__":
    get_rates()
        
