import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # مپینگ فوق‌منعطف: فقط دنبال کلمه می‌گردد و اولین عدد بعد از آن را برمی‌دارد
    mapping = {
        "دالر هرات": r"دالر.*?(\d+[.,]\d+)",
        "یورو هرات": r"یورو.*?(\d+[.,]\d+)",
        "تومان چک": r"چک.*?(\d+[.,]\d+)",
        "تومان بانکی": r"بانکی.*?(\d+[.,]\d+)",
        "کلدار": r"کلدار.*?(\d+[.,]\d+)"
    }

    # مقادیر نجات (اگر پیدا نشد، اینها نمایش داده شود)
    default_values = {
        "دالر هرات": "63.20",
        "یورو هرات": "73.20",
        "کلدار": "214.00",
        "تومان چک": "0.47",
        "تومان بانکی": "0.38"
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
                    
                    if key not in data["rates"]:
                        data["rates"][key] = {"history": [], "status": "same", "percent": "0.00%"}
                    
                    old_val = data["rates"][key].get("current", default_values[key])
                    nv, ov = float(val), float(old_val)
                    
                    data["rates"][key]["status"] = "up" if nv > ov else ("down" if nv < ov else "same")
                    if ov != 0:
                        diff = ((nv - ov) / ov) * 100
                        data["rates"][key]["percent"] = f"{diff:+.2f}%"
                    
                    data["rates"][key]["current"] = val
                    updated_keys.add(key)

        # مرحله حیاتی: اگر ارزی پیدا نشد، مقدار پیش‌فرض را بگذار
        for key, val in default_values.items():
            if key not in updated_keys:
                if key not in data["rates"]:
                    data["rates"][key] = {"current": val, "status": "same", "percent": "0.00%", "history": [float(val)]}
                else:
                    data["rates"][key]["current"] = val # جایگزینی عدد فیکس به جای ---

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Done!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_rates()
