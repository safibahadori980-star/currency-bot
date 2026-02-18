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
    
    # مپینگ ترکیبی (ایموجی یا کلمه کلیدی)
    mapping = {
        "دالر هرات": ["💵", "دالر"],
        "یورو هرات": ["💶", "یورو"],
        "تومان چک": ["💎", "تومان چک"],
        "کلدار": ["🇵🇰", "کلدار"],
        "تومان بانکی": ["💳", "تومان بانکی"]
    }

    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: data = {"rates": {}}
    else: data = {"rates": {}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        found_in_this_run = set()

        # بررسی ۱۵۰ پیام آخر برای اینکه حتماً یورو رو پیدا کنه (چون یورو کمه)
        for msg in reversed(messages[-150:]):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, keys in mapping.items():
                if site_key not in found_in_this_run:
                    # چک کردن اینکه آیا ایموجی یا کلمه در متن هست
                    if any(k in text for k in keys):
                        # پیدا کردن اولین عدد
                        match = re.search(r'(\d+[\.,]\d+|\d+)', text)
                        if match:
                            new_val = match.group(1).replace(',', '.')
                            
                            if site_key in data.get("rates", {}):
                                old_val_str = data["rates"][site_key].get("current", "---")
                                if old_val_str != "---":
                                    try:
                                        old_v, new_v = float(old_val_str), float(new_val)
                                        if new_v > old_v: data["rates"][site_key]["status"] = "up"
                                        elif new_v < old_v: data["rates"][site_key]["status"] = "down"
                                        else: data["rates"][site_key]["status"] = "same"
                                        data["rates"][site_key]["percent"] = f"{((new_v - old_v) / old_v) * 100:+.2f}%"
                                    except: pass
                            else:
                                data["rates"][site_key] = {"status": "same", "percent": "0.00%"}

                            data["rates"][site_key]["current"] = new_val
                            found_in_this_run.add(site_key)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ موارد یافت شده: {list(found_in_this_run)}")

    except Exception as e: print(f"🔥 خطا: {e}")

if __name__ == "__main__":
    get_rates()
                
