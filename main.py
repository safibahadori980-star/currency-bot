import os
import json
import requests
import re
from bs4 import BeautifulSoup

def get_rates():
    url = "https://t.me/s/NerkhYab_Khorasan"
    file_name = 'last_rates.json'

    # مپینگ هوشمند: کلمه را پیدا کن، کلمات اضافی را نادیده بگیر و عدد دوم (فروش) را بردار
    # الگو: کلمه کلیدی + هر چیزی تا عدد اول + هر چیزی تا عدد دوم
    mapping = {
        "دالر هرات": r"دالر.*?(\d+[.,]\d+).*?(\d+[.,]\d+)",
        "یورو هرات": r"یورو.*?(\d+[.,]\d+).*?(\d+[.,]\d+)",
        "تومان چک": r"چک.*?(\d+[.,]\d+).*?(\d+[.,]\d+)",
        "تومان بانکی": r"بانکی.*?(\d+[.,]\d+).*?(\d+[.,]\d+)",
        "کلدار": r"کلدار.*?(\d+[.,]\d+).*?(\d+[.,]\d+)"
    }

    # خواندن دیتای قبلی
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

        # انتخاب ۱۰۰ پیام آخر و پیمایش از جدیدترین به قدیمی‌ترین
        recent_messages = list(reversed(messages[-100:]))
        
        updated_in_this_run = set()

        for msg in recent_messages:
            text = msg.get_text(separator=" ").replace('\n', ' ')
            
            for site_key, pattern in mapping.items():
                # اگر در این دور اجرا، این ارز قبلاً با قیمت جدیدتر پیدا شده، دیگر جستجو نکن
                if site_key in updated_in_this_run:
                    continue
                
                match = re.search(pattern, text)
                if match:
                    # انتخاب عدد دوم (قیمت فروش) - اگر نبود عدد اول را برمی‌دارد
                    val_str = match.group(2) if match.group(2) else match.group(1)
                    new_val = val_str.replace(',', '.')

                    # فیلتر برای جلوگیری از ثبت اعداد پرت و اشتباه
                    if (site_key == "دالر هرات" or site_key == "یورو هرات") and float(new_val) < 10:
                        continue

                    if site_key not in data["rates"]:
                        data["rates"][site_key] = {"history": [], "status": "same", "percent": "0.00%"}
                    
                    old_val = data["rates"][site_key].get("current", "0")
                    
                    if old_val != new_val:
                        nv = float(new_val)
                        ov = float(old_val) if old_val not in ["0", "---"] else nv
                        
                        # تعیین وضعیت صعودی/نزولی
                        if nv > ov: data["rates"][site_key]["status"] = "up"
                        elif nv < ov: data["rates"][site_key]["status"] = "down"
                        
                        # محاسبه درصد نوسان
                        if ov != 0:
                            diff = ((nv - ov) / ov) * 100
                            data["rates"][site_key]["percent"] = f"{diff:+.2f}%"
                        
                        data["rates"][site_key]["current"] = new_val
                        
                        # آپدیت تاریخچه نمودار
                        hist = data["rates"][site_key].get("history", [])
                        if not hist or hist[-1] != nv:
                            hist.append(nv)
                            if len(hist) > 15: hist.pop(0)
                        data["rates"][site_key]["history"] = hist
                    
                    updated_in_this_run.add(site_key)

        # ذخیره در فایل
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print("بروزرسانی با موفقیت انجام شد.")

    except Exception as e:
        print(f"خطا در اجرای اسکرپر: {e}")

if __name__ == "__main__":
    get_rates()
