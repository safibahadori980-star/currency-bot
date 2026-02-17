import requests
from bs4 import BeautifulSoup
import json
import os
import re

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    
    # مپینگ نهایی بر اساس پیام‌های کانال شما
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار (پاکستان)": "کلدار افغانی"
    }

    file_name = 'last_rates.json'
    
    # ۱. خواندن دیتای قبلی برای حفظ نرخ‌هایی که پیام جدید ندارند (مثل یورو)
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}
    else:
        data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        # ۲. بررسی ۵۰ پیام آخر برای پوشش دادن نرخ‌های قدیمی‌تر
        target_messages = messages[-50:] if len(messages) > 50 else messages
        
        found_keys = set()
        for msg in reversed(target_messages):
            text = " ".join(msg.get_text().split())
            
            for site_key, telegram_key in mapping.items():
                if site_key not in found_keys and telegram_key in text:
                    # استخراج عدد (معمولاً نرخ فروش که دومین یا آخرین عدد است)
                    prices = re.findall(r'(\d+[.,]?\d*)', text)
                    if prices:
                        new_val = prices[-1].replace(',', '.')
                        
                        # مقایسه برای جهت فلش (صعودی/نزولی)
                        try:
                            old_val = float(data['rates'][site_key]['current'])
                            if float(new_val) > old_val: data['rates'][site_key]['status'] = "up"
                            elif float(new_val) < old_val: data['rates'][site_key]['status'] = "down"
                        except: pass
                        
                        data['rates'][site_key]['current'] = new_val
                        found_keys.add(site_key)
            
            if len(found_keys) == len(mapping):
                break

        # ۳. ذخیره نهایی
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ انجام شد! نرخ‌های آپدیت شده در این مرحله: {list(found_keys)}")

    except Exception as e:
        print(f"❌ خطا در اجرا: {e}")

if __name__ == "__main__":
    get_rates()
