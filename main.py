import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # مپینگ منعطف برای پیدا کردن اعداد
    mapping = {
        "دالر هرات": r"دالر.*?(\d+[.,]\d+)",
        "یورو هرات": r"یورو.*?(\d+[.,]\d+)",
        "تومان چک": r"چک.*?(\d+[.,]\d+)",
        "تومان بانکی": r"بانکی.*?(\d+[.,]\d+)",
        "کلدار": r"کلدار.*?(\d+[.,]\d+)"
    }

    # مقادیر پیش‌فرض اگر در پیام‌ها پیدا نشدند
    default_rates = {
        "کلدار": "214.00",
        "یورو هرات": "73.20",
        "دالر هرات": "63.20",
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')

        recent_messages = list(reversed(messages[-100:]))
        updated_keys = set()

        for msg in recent_messages:
            text = " ".join(msg.get_text(separator=" ").replace('\n', ' ').split())
            
            for site_key, pattern in mapping.items():
                if site_key in updated_keys: continue
                
                match = re.search(pattern, text)
                if match:
                    new_val = match.group(1).replace(',', '.')
                    
                    if site_key not in data["rates"]:
                        data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                    
                    old_val = data["rates"][site_key].get("current", default_rates.get(site_key, "0"))
                    
                    if old_val != new_val:
                        nv, ov = float(new_val), float(old_val)
                        data["rates"][site_key]["status"] = "up" if nv > ov else ("down" if nv < ov else "same")
                        if ov != 0:
                            diff = ((nv - ov) / ov) * 100
                            data["rates"][site_key]["percent"] = f"{diff:+.2f}%"
                        
                        data["rates"][site_key]["current"] = new_val
                        hist = data["rates"][site_key].get("history", [])
                        if not hist or hist[-1] != nv:
                            hist.append(nv)
                            if len(hist) > 15: hist.pop(0)
                        data["rates"][site_key]["history"] = hist
                    
                    updated_keys.add(site_key)

        # اضافه کردن مقادیر پیش‌فرض برای مواردی که پیدا نشدند
        for key, val in default_rates.items():
            if key not in data["rates"] or data["rates"][key].get("current") == "---":
                data["rates"][key] = {
                    "current": val,
                    "status": "same",
                    "percent": "0.00%",
                    "history": [float(val)]
                }

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("بروزرسانی انجام شد.")

    except Exception as e:
        print(f"خطا: {e}")

if __name__ == "__main__":
    get_rates()
