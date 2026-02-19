import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # هماهنگی نام‌ها با کلیدهای کد HTML شما
    mapping = {
        "دالر هرات": ["دالر"],
        "یورو هرات": ["یورو"],
        "تومان چک": ["تومان چک"],
        "کلدار": ["کلدار"],
        "تومان بانکی": ["تومان بانکی"]
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
        for msg in reversed(messages[-20:]): # بررسی ۲۰ پیام آخر
            text = msg.get_text(separator=" ").replace('\n', ' ').replace(',', '.')
            
            for site_key, keywords in mapping.items():
                if site_key not in found_keys and any(k in text for k in keywords):
                    # استخراج تمام اعداد موجود در خط (خرید و فروش)
                    numbers = re.findall(r'(\d+\.\d+|\d+)', text)
                    
                    if len(numbers) >= 2:
                        buy_val = numbers[0]
                        sell_val = numbers[1]
                        
                        if site_key not in data["rates"]:
                            data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                        
                        old_buy = data["rates"][site_key].get("buy", "0")
                        
                        # بروزرسانی مقادیر
                        data["rates"][site_key]["buy"] = buy_val
                        data["rates"][site_key]["sell"] = sell_val
                        
                        # محاسبه وضعیت صعودی/نزولی
                        nb, ob = float(buy_val), float(old_buy)
                        if nb > ob: data["rates"][site_key]["status"] = "up"
                        elif nb < ob: data["rates"][site_key]["status"] = "down"
                        
                        if ob != 0:
                            data["rates"][site_key]["percent"] = f"{((nb-ob)/ob)*100:+.2f}%"

                        # بروزرسانی تاریخچه نمودار
                        hist = data["rates"][site_key].get("history", [])
                        if not hist or hist[-1] != nb:
                            hist.append(nb)
                        if len(hist) > 10: hist.pop(0)
                        data["rates"][site_key]["history"] = hist
                        
                        found_keys.add(site_key)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Done: {list(found_keys)}")

    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    get_rates()
