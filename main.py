import os
import json
import requests
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system('pip install beautifulsoup4')
    from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    
    # کلمات کلیدی را کوتاه کردیم تا حساسیت کمتر شود
    mapping = {
        "دالر هرات": "دالر افغانی",
        "یورو هرات": "یورو افغانی",
        "تومان چک": "تومان چک",
        "تومان بانکی": "تومان بانکی",
        "کلدار": "کلدار افغانی"
    }

    file_name = 'last_rates.json'
    data = {"rates": {k: {"current": "---", "status": "up", "percent": "0.00%"} for k in mapping.keys()}}

    # خواندن مقادیر قبلی برای محاسبه درصد و نوسان
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except: old_data = {"rates": {}}
    else: old_data = {"rates": {}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        found_count = 0
        for msg in reversed(messages[-60:]):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            for site_key, telegram_key in mapping.items():
                if telegram_key in text and data["rates"][site_key]["current"] == "---":
                    # پیدا کردن اولین عدد قبل از کلمه "خرید" یا اولین عدد در پیام
                    match = re.search(r'(\d+[\.,]\d+|\d+)', text)
                    if match:
                        new_val = match.group(1).replace(',', '.')
                        data["rates"][site_key]["current"] = new_val
                        
                        # محاسبه نوسان و درصد (اگر دیتای قبلی بود)
                        if site_key in old_data.get("rates", {}):
                            try:
                                old_val = float(old_data["rates"][site_key]["current"])
                                current_val = float(new_val)
                                diff = current_val - old_val
                                
                                if diff > 0: data["rates"][site_key]["status"] = "up"
                                elif diff < 0: data["rates"][site_key]["status"] = "down"
                                else: data["rates"][site_key]["status"] = old_data["rates"][site_key].get("status", "up")
                                
                                # محاسبه درصد نوسان
                                if old_val != 0:
                                    percent = (diff / old_val) * 100
                                    data["rates"][site_key]["percent"] = f"{percent:+.2f}%"
                            except: pass
                        
                        found_count += 1
            if found_count == len(mapping): break

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ بروزرسانی موفق: {found_count} مورد")

    except Exception as e: print(f"🔥 خطا: {e}")

if __name__ == "__main__":
    get_rates()
