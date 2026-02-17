import requests
from bs4 import BeautifulSoup
import json
import os
import re

def get_rates():
    # آدرس نسخه وب کانال برای دور زدن محدودیت ادمین
    url = "https://t.me/s/NerkhYab_Khorasan"
    
    # مپینگ کلمات کلیدی (دقیقاً مشابه پیام‌های کانال شما)
    mapping = {
        "دالر هرات": "هرات دالر",
        "یورو هرات": "هرات یورو",
        "تومان چک": "تومان چک",
        "تومان بانکی": "تومان بانکی",
        "کلدار افغانی": "کلدار"
    }

    file_name = 'last_rates.json'
    
    # ساختار اولیه دیتا
    data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    # بارگذاری دیتای قبلی برای مقایسه قیمت (صعودی/نزولی)
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: pass

    print("Connecting to Telegram...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        if not messages:
            print("❌ محتوایی یافت نشد. احتمالاً آی‌پی مسدود است.")
            return

        updated = False
        # بررسی پیام‌ها از جدیدترین به قدیمی‌ترین
        for msg in reversed(messages):
            text = msg.get_text()
            for site_key, telegram_key in mapping.items():
                if telegram_key in text:
                    # استخراج عدد (پشتیبانی از فرمت 63.25 یا 63,25)
                    price_match = re.findall(r'(\d+[.,]?\d*)', text)
                    if price_match:
                        new_val = price_match[-1].replace(',', '.')
                        
                        # تشخیص وضعیت بالا یا پایین رفتن قیمت
                        try:
                            old_val = float(data['rates'][site_key]['current'])
                            if float(new_val) > old_val: data['rates'][site_key]['status'] = "up"
                            elif float(new_val) < old_val: data['rates'][site_key]['status'] = "down"
                        except: pass
                        
                        data['rates'][site_key]['current'] = new_val
                        updated = True
            if updated: break

        if updated:
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("✅ قیمت‌ها با موفقیت بروزرسانی شدند.")
        else:
            print("⚠️ کلمات کلیدی در پیام‌های اخیر پیدا نشدند.")

    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    get_rates()
