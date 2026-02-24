import os
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'
    now = datetime.now()

    mapping = {
        "دالر هرات": r"دالر.*?(\d+[.,]\d+)",
        "یورو هرات": r"یورو.*?(\d+[.,]\d+)",
        "تومان چک": r"چک.*?(\d+[.,]\d+)",
        "تومان بانکی": r"بانکی.*?(\d+[.,]\d+)",
        "کلدار": r"کلدار.*?(\d+[.,]\d+)"
    }

    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "rates" not in data: data = {"rates": {}}
        except: data = {"rates": {}}
    else:
        data = {"rates": {}}

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        recent_messages = list(reversed(messages[-100:]))
        updated_keys = set()

        for msg in recent_messages:
            text = msg.get_text(separator=" ").replace('\n', ' ')
            for key, pattern in mapping.items():
                if key in updated_keys: continue
                match = re.search(pattern, text)
                if match:
                    val = match.group(1).replace(',', '.')
                    nv = float(val)
                    
                    if key not in data["rates"]:
                        data["rates"][key] = {"history": [nv], "status": "up", "percent": "0.00%"}
                    
                    # پاکسازی تاریخچه قدیمی در ابتدای روز (ساعت ۱۲ شب)
                    if now.hour == 0 and now.minute < 10:
                        data["rates"][key]["history"] = [nv]

                    # قیمت مبنا = اولین قیمت ثبت شده در لیست (قیمت صبح)
                    base_price = float(data["rates"][key]["history"][0])
                    
                    # رنگ فلش: اگر از صبح بالاتر بود سبز، اگر پایین‌تر بود قرمز
                    data["rates"][key]["status"] = "up" if nv >= base_price else "down"
                    
                    # محاسبه درصد نوسان کل روز
                    diff = ((nv - base_price) / base_price * 100) if base_price != 0 else 0
                    data["rates"][key]["percent"] = f"{diff:+.2f}%"
                    
                    data["rates"][key]["current"] = val
                    updated_keys.add(key)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Success! Updated at {now.strftime('%H:%M')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_rates()
