import requests
from bs4 import BeautifulSoup
import json
import os
import re

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار (پاکستان)": "هرات کلدار افغانی"
    }

    file_name = 'last_rates.json'
    
    # خواندن دیتای قبلی
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
        
        target_messages = messages[-50:]
        
        found_keys = set()
        for msg in reversed(target_messages):
            # تبدیل متن پیام به یک خط صاف و تمیز کردن فاصله‌ها
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, telegram_key in mapping.items():
                if site_key not in found_keys and telegram_key in text:
                    # ۱. پیدا کردن تمام اعدادی که ممکن است کاما داشته باشند (مثل 62,95 یا 214.00)
                    raw_prices = re.findall(r'\d+[\.,]\d+', text)
                    
                    if raw_prices:
                        # ۲. تبدیل کاما به نقطه برای محاسبات ریاضی
                        clean_prices = [p.replace(',', '.') for p in raw_prices]
                        
                        # ۳. طبق متن پیام شما، عدد دوم همیشه "فروش" است
                        # اگر یک عدد بود همان را بردار، اگر بیشتر بود دومی (فروش) را بردار
                        new_val = clean_prices[1] if len(clean_prices) > 1 else clean_prices[0]
                        
                        # ۴. تشخیص وضعیت صعودی/نزولی
                        try:
                            old_val = float(data['rates'][site_key]['current'])
                            if float(new_val) > old_val: data['rates'][site_key]['status'] = "up"
                            elif float(new_val) < old_val: data['rates'][site_key]['status'] = "down"
                        except: pass
                        
                        data['rates'][site_key]['current'] = new_val
                        found_keys.add(site_key)
            
            if len(found_keys) == len(mapping):
                break

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ نرخ‌های جدید با موفقیت استخراج شد: {list(found_keys)}")

    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    get_rates()
