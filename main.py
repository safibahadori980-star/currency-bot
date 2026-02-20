import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # مپینگ ساده و مستقیم
    mapping = {
        "دالر هرات": ["دالر", "دلار"],
        "یورو هرات": ["یورو"],
        "تومان چک": ["چک"],
        "کلدار": ["کلدار"],
        "تومان بانکی": ["بانکی"]
    }

    # خواندن داده‌های قبلی برای جلوگیری از حذف
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
        
        # بررسی ۱۰۰ پیام اخیر
        for msg in reversed(messages[-100:]):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, keywords in mapping.items():
                # اگر ارز پیدا نشده و یکی از کلمات کلیدی در متن هست
                if site_key not in found_in_this_run and any(k in text for k in keywords):
                    
                    # استخراج تمام اعداد موجود در آن پیام (با پشتیبانی از نقطه و کاما)
                    # خروجی مثلا می‌شود: ['73.20', '73.50']
                    numbers = re.findall(r'\d+[.,]\d+|\d+', text)
                    
                    if numbers:
                        # طبق درخواست شما: فقط اولین عدد (نرخ خرید) را بردار
                        buy_val = numbers[0].replace(',', '.')
                        
                        if site_key not in data["rates"]:
                            data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                        
                        old_val = data["rates"][site_key].get("current", "0")
                        
                        # بروزرسانی مقدار فعلی
                        data["rates"][site_key]["current"] = buy_val
                        data["rates"][site_key]["buy"] = buy_val
                        
                        # محاسبه نوسان نسبت به نرخ قبلی
                        try:
                            ov = float(old_val) if old_val not in ["---", "0"] else 0
                            nv = float(buy_val)
                            if ov != 0 and nv != ov:
                                data["rates"][site_key]["status"] = "up" if nv > ov else "down"
                                data["rates"][site_key]["percent"] = f"{((nv-ov)/ov)*100:+.2f}%"
                        except: pass

                        # اضافه کردن به تاریخچه نمودار
                        hist = data["rates"][site_key].get("history", [])
                        if not hist or hist[-1] != float(buy_val):
                            hist.append(float(buy_val))
                            if len(hist) > 15: hist.pop(0)
                        data["rates"][site_key]["history"] = hist
                        
                        found_in_this_run.add(site_key)

        # ذخیره نهایی در فایل (خارج از حلقه برای جلوگیری از پریدن داده‌ها)
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"آپدیت موفقیت‌آمیز بود. موارد پیدا شده: {list(found_in_this_run)}")

    except Exception as e: 
        print(f"خطا در اجرای اسکریپت: {e}")

if __name__ == "__main__":
    get_rates()
