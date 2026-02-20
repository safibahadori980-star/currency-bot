import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # کلمات کلیدی دقیق بر اساس فرمت کانال شما
    mapping = {
        "دالر هرات": ["دالر", "دلار"],
        "یورو هرات": ["یورو"],
        "تومان چک": ["تومان چک", "چک هرات"],
        "کلدار": ["کلدار"],
        "تومان بانکی": ["تومان بانکی", "تومان ایران"]
    }

    # ۱. بارگذاری داده‌های قبلی (برای جلوگیری از حذف شدن ارزهای غایب)
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
        
        # ۲. بررسی ۱۰۰ پیام اخیر از جدید به قدیم
        for msg in reversed(messages[-100:]):
            # تمیزکاری متن: تبدیل کاما به نقطه و ایجاد فاصله بین اعداد و حروف چسبیده
            raw_text = msg.get_text(separator=" ").replace(',', '.')
            text = re.sub(r'(\d+)([^\d\s\.])', r'\1 \2', raw_text)
            
            for site_key, keywords in mapping.items():
                # اگر این ارز را در این دور هنوز پیدا نکردیم و کلمه کلیدی در متن هست
                if site_key not in found_in_this_run and any(k in text for k in keywords):
                    # استخراج اعداد اعشاری یا صحیح
                    numbers = re.findall(r'\d+\.\d+|\d+', text)
                    if numbers:
                        # در فرمت پیام‌های شما، اولین عدد نرخ خرید است
                        buy_val = numbers[0]
                        
                        # ایجاد ساختار اگر قبلاً وجود نداشته باشد
                        if site_key not in data["rates"]:
                            data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                        
                        old_val = data["rates"][site_key].get("current", "0")
                        
                        # ۳. فقط اگر قیمت تغییر کرده باشد آپدیت کن
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

                            # آپدیت نمودار
                            hist = data["rates"][site_key].get("history", [])
                            if not hist or hist[-1] != float(buy_val):
                                hist.append(float(buy_val))
                            if len(hist) > 15: hist.pop(0)
                            data["rates"][site_key]["history"] = hist
                        
                        found_in_this_run.add(site_key)

        # ۴. ذخیره نهایی (ارزهایی که پیدا نشدند، با قیمت قبلی در فایل می‌مانند)
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Update Success. Found now: {list(found_in_this_run)}")
        print(f"Total currencies in file: {list(data['rates'].keys())}")

    except Exception as e: 
        print(f"Error: {e}")

if __name__ == "__main__":
    get_rates()
