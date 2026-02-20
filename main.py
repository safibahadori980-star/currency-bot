import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # مپینگ بسیار ساده برای جلوگیری از خطا
    mapping = {
        "دالر هرات": ["دالر", "دلار"],
        "یورو هرات": ["یورو"],
        "تومان چک": ["چک"],
        "کلدار": ["کلدار"],
        "تومان بانکی": ["بانکی"]
    }

    # ۱. خواندن دیتای قدیمی (بسیار مهم برای نپریدن ارزها)
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("Old data loaded successfully.")
        except: 
            data = {"rates": {}}
    else: 
        data = {"rates": {}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')

        found_in_this_run = set()
        
        # بررسی ۱۰۰ پیام آخر
        for msg in reversed(messages[-100:]):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, keywords in mapping.items():
                if site_key not in found_in_this_run and any(k in text for k in keywords):
                    # پیدا کردن اعداد (پشتیبانی از 73,20 و 214.00)
                    numbers = re.findall(r'\d+[.,]\d+|\d+', text)
                    if numbers:
                        buy_val = numbers[0].replace(',', '.')
                        
                        # اگر ارز از قبل نبود، ساختارش را بساز
                        if site_key not in data["rates"]:
                            data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                        
                        old_val = data["rates"][site_key].get("current", "0")
                        
                        # آپدیت مقادیر
                        data["rates"][site_key]["current"] = buy_val
                        data["rates"][site_key]["buy"] = buy_val
                        
                        # محاسبه نوسان
                        try:
                            ov, nv = float(old_val if old_val not in ["---", "0"] else 0), float(buy_val)
                            if ov != 0 and nv != ov:
                                data["rates"][site_key]["status"] = "up" if nv > ov else "down"
                                data["rates"][site_key]["percent"] = f"{((nv-ov)/ov)*100:+.2f}%"
                        except: pass

                        # آپدیت هیستوری
                        hist = data["rates"][site_key].get("history", [])
                        if not hist or hist[-1] != float(buy_val):
                            hist.append(float(buy_val))
                            if len(hist) > 15: hist.pop(0)
                        data["rates"][site_key]["history"] = hist
                        
                        found_in_this_run.add(site_key)

        # ۲. ذخیره نهایی (تراز شده در بیرونی‌ترین لایه برای امنیت کامل)
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Update Success. Found: {list(found_in_this_run)}")
        print(f"Current file keys: {list(data['rates'].keys())}")

    except Exception as e: 
        print(f"Error: {e}")

if __name__ == "__main__":
    get_rates()
