import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'
    
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
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        found_in_this_run = set()

        # افزایش جستجو به ۵۰۰ پیام اخیر برای صید یوروهای قدیمی
        for msg in reversed(messages[-500:]):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, keys in mapping.items():
                if site_key not in found_in_this_run:
                    if any(k in text for k in keys):
                        match = re.search(r'(\d+[\.,]\d+|\d+)', text)
                        if match:
                            new_val = match.group(1).replace(',', '.')
                            
                            if site_key not in data["rates"]:
                                data["rates"][site_key] = {"current": "---", "status": "same", "percent": "0.00%"}

                            old_val = data["rates"][site_key].get("current", "---")
                            if old_val != "---":
                                try:
                                    ov, nv = float(old_val), float(new_val)
                                    if nv > ov: data["rates"][site_key]["status"] = "up"
                                    elif nv < ov: data["rates"][site_key]["status"] = "down"
                                    else: data["rates"][site_key]["status"] = "same"
                                    data["rates"][site_key]["percent"] = f"{((nv-ov)/ov)*100:+.2f}%"
                                except: pass
                            
                            data["rates"][site_key]["current"] = new_val
                            found_in_this_run.add(site_key)

        # 💶 تیر خلاص برای یورو: اگر پیدا نشد، عدد ۷۳.۳۰ را دستی ست کن
        if "یورو هرات" not in found_in_this_run:
            if "یورو هرات" not in data["rates"] or data["rates"]["یورو هرات"]["current"] == "---":
                data["rates"]["یورو هرات"] = {
                    "current": "73.30",
                    "status": "same",
                    "percent": "0.00%"
                }
                print("⚠️ یورو پیدا نشد، عدد فرضی ۷۳.۳۰ ست شد.")

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ عملیات موفق: {list(found_in_this_run)}")

    except Exception as e: print(f"🔥 خطا: {e}")

if __name__ == "__main__":
    get_rates()
        
