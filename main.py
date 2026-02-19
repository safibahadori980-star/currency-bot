import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    mapping = {
        "دالر هرات": ["دالر", "دلار"],
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')

        found_keys = set()
        for msg in reversed(messages[-100:]):
            text = msg.get_text(separator=" ").replace('\n', ' ').replace(',', '.')
            
            for site_key, keywords in mapping.items():
                if site_key not in found_keys and any(k in text for k in keywords):
                    numbers = re.findall(r'(\d+\.\d+|\d+)', text)
                    if numbers:
                        buy_val = numbers[0]
                        sell_val = numbers[1] if len(numbers) > 1 else buy_val
                        
                        if site_key not in data["rates"]:
                            data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                        
                        old_val = data["rates"][site_key].get("current", "0")
                        
                        # ذخیره مقادیر (هم Current هم Buy برای احتیاط)
                        data["rates"][site_key]["current"] = buy_val
                        data["rates"][site_key]["buy"] = buy_val
                        data["rates"][site_key]["sell"] = sell_val
                        
                        try:
                            ov, nv = float(old_val if old_val != "---" else 0), float(buy_val)
                            if ov != 0:
                                if nv > ov: data["rates"][site_key]["status"] = "up"
                                elif nv < ov: data["rates"][site_key]["status"] = "down"
                                data["rates"][site_key]["percent"] = f"{((nv-ov)/ov)*100:+.2f}%"
                        except: pass

                        hist = data["rates"][site_key].get("history", [])
                        if not hist or hist[-1] != float(buy_val):
                            hist.append(float(buy_val))
                        if len(hist) > 15: hist.pop(0)
                        data["rates"][site_key]["history"] = hist
                        
                        found_keys.add(site_key)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Update Success: {list(found_keys)}")

    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    get_rates()
