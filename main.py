import requests
from bs4 import BeautifulSoup
import json
import os
import re

def get_rates():
    # آدرس نسخه وب کانال برای خواندن پیام‌ها بدون نیاز به عضویت
    url = "https://t.me/s/NerkhYab_Khorasan"
    
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار افغانی": "هرات کلدار افغانی"
    }

    file_name = 'last_rates.json'
    # آماده‌سازی ساختار فایل
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    print("در حال خواندن اطلاعات از صفحه عمومی کانال...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # پیدا کردن تمام پیام‌های کانال
    messages = soup.find_all('div', class_='tgme_widget_message_text')
    
    updated = False
    # بررسی پیام‌ها از جدید به قدیم
    for msg in reversed(messages):
        text = msg.get_text()
        for site_key, telegram_key in mapping.items():
            if telegram_key in text:
                lines = text.split('\n')
                for line in lines:
                    if "فروش" in line:
                        price_match = re.findall(r'\d+[.,]?\d*', line)
                        if price_match:
                            new_val = price_match[-1].replace(',', '')
                            data['rates'][site_key]['current'] = new_val
                            updated = True
        if updated: break # اگر آخرین پیام قیمت را پیدا کردیم، کافیست

    if updated:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ عالی شد! قیمت‌ها بدون نیاز به ربات و ادمین، آپدیت شدند.")
    else:
        print("❌ متاسفانه قیمتی در صفحه پیدا نشد.")

if __name__ == "__main__":
    get_rates()
