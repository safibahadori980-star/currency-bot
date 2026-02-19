import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # مپینگ نام‌ها برای هماهنگی با متن کانال و فایل شما
    mapping = {
        "دالر هرات": ["دالر"],
        "یورو هرات": ["یورو"],
        "تومان چک": ["تومان چک"],
        "کلدار": ["کلدار"],
        "تومان بانکی": ["تومان بانکی"]
    }

    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: data = {"rates": {}}
    else: data = {"rates": {}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')

        found_in_this_run = set()

        # بررسی ۵۰ پیام آخر برای پیدا کردن جدیدترین نرخ‌ها
        for msg in reversed(messages[-50:]):
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, keys in mapping.items():
                if site_key not in found_in_this_run:
                    # الگوی جدید برای استخراج هر دو قیمت خرید و فروش
                    # این الگو دنبال اعدادی می‌گردد که قبل از کلمه خرید و فروش هستند
                    match = re.findall(r'(\d+[.,]\d+)', text)
                    
                    # اگر کلمه کلیدی (مثل یورو) در متن بود
                    if any(k in text for k in keys):
                        if len(match) >= 2:
                            # پاکسازی اعداد (تبدیل کاما به نقطه)
                            buy_val = match[0].replace(',', '.')
                            sell_val = match[1].replace(',', '.')
                            
                            if site_key not in data["rates"]:
                                data["rates"][site_key] = {"buy": "---", "sell": "---", "status": "same", "percent": "0.00%", "history": []}
                            
                            old_buy = data["rates"][site_key].get("buy", "---")
                            
                            # محاسبه روند تغییرات (Status)
                            if old_buy != "---":
                                try:
                                    ob = float(old_buy)
                                    nb = float(buy_val)
                                    if nb > ob: data["rates"][site_key]["status"] = "up"
                                    elif nb < ob: data["rates"][site_key]["status"] = "down"
                                    data["rates"][site_key]["percent"] = f"{((nb-ob)/ob)*100:+.2f}%"
                                except: pass
                            
                            data["rates"][site_key]["buy"] = buy_val
                            data["rates"][site_key]["sell"] = sell_val
                            
                            # اضافه کردن به تاریخچه برای نمودار منحنی
                            hist = data["rates"][site_key].get("history", [])
                            if not hist or hist[-1] != float(buy_val):
                                hist.append(float(buy_val))
                            if len(hist) > 10: hist.pop(0)
                            data["rates"][site_key]["history"] = hist
                            
                            found_in_this_run.add(site_key)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ عملیات موفق: {list(found_in_this_run)}")

    except Exception as e: print(f"🔥 خطا: {e}")

if __name__ == "__main__":
    get_rates()
