import os
import json
import requests
from bs4 import BeautifulSoup
import re

def get_rates():
    print("🚀 شروع عملیات دریافت نرخ...")
    url = "https://t.me/s/NerkhYab_Khorasan"
    
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار": "هرات کلدار افغانی"
    }

    file_name = 'last_rates.json'
    
    # دیتای پیش‌فرض
    data = {"rates": {k: {"current": "---", "status": "up"} for k in mapping.keys()}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"❌ خطا: تلگرام پاسخ نداد (کد {response.status_code})")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        if not messages:
            print("❌ هیچ پیامی در کانال پیدا نشد!")
            return

        found_count = 0
        for msg in reversed(messages[-40:]):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            for site_key, telegram_key in mapping.items():
                if telegram_key in text and data["rates"][site_key]["current"] == "---":
                    match = re.search(r'(\d+[\.,]\d+|\d+)\s+خرید', text)
                    if match:
                        data["rates"][site_key]["current"] = match.group(1).replace(',', '.')
                        found_count += 1
            if found_count == len(mapping): break

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ موفقیت! {found_count} نرخ بروزرسانی شد.")

    except Exception as e:
        print(f"🔥 ارور سیستمی: {str(e)}")

if __name__ == "__main__":
    get_rates()
