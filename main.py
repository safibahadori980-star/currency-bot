import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # کلمات کلیدی برای جستجو در تلگرام
    mapping = {
        "دالر هرات": ["دالر", "دلار"],
        "یورو هرات": ["یورو"],
        "تومان چک": ["تومان چک", "چک هرات"],
        "کلدار": ["کلدار"],
        "تومان بانکی": ["تومان بانکی", "تومان ایران"]
    }

    # خواندن داده‌های قبلی برای حفظ ارزهای غایب
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
        
        # بررسی پیام‌ها از جدید به قدیم
        for msg in reversed(messages[-100:]): # بررسی ۵۰ پیام آخر برای اطمینان بیشتر
            text = msg.get_text(separator=" ").replace('\n', ' ').replace(',', '.')
            
            for site_key, keywords in mapping.items():
                # اگر این ارز را قبلاً در این دور پیدا نکردیم و کلمه کلیدی در متن هست
                if site_key not in found_in_this_run and any(k in text for k in keywords):
                    numbers = re.findall(r'(\d+\.\d+|\d+)', text)
                    if numbers:
                        # استخراج قیمت (معمولاً اولین عدد قیمت خرید است)
                        buy_val = numbers[0]
                        
                        # اگر ارز از قبل در دیتابیس نبود، ساختار اولیه را بساز
                        if site_key not in data["rates"]:
                            data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                        
                        old_val = data["rates"][site_key].get("current", "0")
                        
                        # فقط اگر قیمت واقعاً تغییر کرده باشد آپدیت کن
                        if old_val != buy_val:
                            data["rates"][site_key]["current"] = buy_val
                            data["rates"][site_key]["buy"] = buy_val
                            
                            try:
                                ov = float(old_val) if old_val not in ["---", "0"] else 0
                                nv = float(buy_val)
                                if ov != 0:
                                    if nv > ov: data["rates"][site_key]["status"] = "up"
                                    elif nv < ov: data["rates"][site_key]["status"] = "down"
                                    data["rates"][site_key]["percent"] = f"{((nv-ov)/ov)*100:+.2f}%"
                            except: pass

                            # آپدیت تاریخچه نمودار
                            hist = data["rates"][site_key].get("history", [])
                            if not hist or hist[-1] != float(buy_val):
                                hist.append(float(buy_val))
                            if len(hist) > 15: hist.pop(0)
                            data["rates"][site_key]["history"] = hist
                        
                        found_in_this_run.add(site_key)

        # ذخیره نهایی (ارزهایی که پیدا نشدند با همان قیمت قبلی در فایل باقی می‌مانند)
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Update Success. Found now: {list(found_in_this_run)}")

    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    get_rates()
