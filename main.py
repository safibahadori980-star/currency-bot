import requests
from bs4 import BeautifulSoup
import json
import os
import re

def get_rates():
    # آدرس کانال تلگرام شما
    url = "https://t.me/s/NerkhYab_Khorasan"
    
    # نقشه کلمات کلیدی (دقیقاً بر اساس متن پیام‌های اسکرین‌شات شما)
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار": "هرات کلدار افغانی"
    }

    file_name = 'last_rates.json'
    
    # دیتای اولیه
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"rates": {}}
    else:
        data = {"rates": {}}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        target_messages = messages[-40:] # بررسی ۴۰ پیام آخر
        found_keys = set()

        for msg in reversed(target_messages):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, telegram_key in mapping.items():
                if site_key not in found_keys and telegram_key in text:
                    # پیدا کردن اعدادی که قبل از کلمه "خرید" هستند
                    # مثل 63,30 در پیام "63,30 خرید"
                    match = re.search(r'(\d+[\.,]\d+|\d+)\s+خرید', text)
                    
                    if match:
                        new_val = match.group(1).replace(',', '.')
                        
                        # ثبت وضعیت تغییر قیمت
                        if site_key in data['rates']:
                            try:
                                old_val = float(data['rates'][site_key]['current'])
                                if float(new_val) > old_val: data['rates'][site_key]['status'] = "up"
                                elif float(new_val) < old_val: data['rates'][site_key]['status'] = "down"
                            except: pass
                        else:
                            data['rates'][site_key] = {"status": "up"}

                        data['rates'][site_key]['current'] = new_val
                        found_keys.add(site_key)

            if len(found_keys) == len(mapping):
                break

        # ذخیره فایل در گیت‌هاب
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ قیمت‌های جدید با موفقیت ثبت شد: {list(found_keys)}")

    except Exception as e:
        print(f"❌ خطا در استخراج: {e}")

if __name__ == "__main__":
    get_rates()
