import re
import json
import os
from telethon import TelegramClient, events

# این مقادیر را در Secrets گیت‌هاب ست کن
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
source_channel = 'NerkhYab_Khorasan'

client = TelegramClient('session_nerkhyab', api_id, api_hash)

# نقشه تطبیق کلمات کانال با کلیدهای سایت شما
mapping = {
    "دالر هرات": "دالر به افغانی",
    "یورو هرات": "یورو به افغانی",
    "تومان چک": "تومان چک",
    "تومان بانکی": "تومان بانکی",
    "کلدار (پاکستان)": "کلدار افغانی"
}

def load_data():
    file_name = 'last_rates.json'
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                pass
    # ساختار اولیه اگر فایل خراب بود یا نبود
    return {"rates": {k: {"current": "---", "status": "up", "diff": "0.0", "history": []} for k in mapping.keys()}}

async def update_json_file(site_name, new_price_str):
    data = load_data()
    file_name = 'last_rates.json'
    
    try:
        # پاکسازی عدد
        clean_price = "".join(re.findall(r'\d+', new_price_str))
        new_price_val = float(clean_price)
        
        # دریافت دیتای قبلی آن ارز
        old_data = data['rates'].get(site_name, {"current": "0", "status": "up", "diff": "0.0", "history": []})
        old_price_str = old_data['current'].replace(',', '')
        old_price_val = float(old_price_str) if old_price_str.isdigit() else new_price_val

        # محاسبه وضعیت
        status = "up" if new_price_val >= old_price_val else "down"
        diff = "0.0"
        if old_price_val != 0:
            diff = str(round(abs((new_price_val - old_price_val) / old_price_val * 100), 2))

        # آپدیت فقط همین یک ارز
        data['rates'][site_name] = {
            "current": "{:,}".format(int(new_price_val)),
            "status": status,
            "diff": diff,
            "history": old_data.get('history', [])
        }
        
        # اضافه کردن به تاریخچه
        data['rates'][site_name]['history'].append(new_price_val)
        if len(data['rates'][site_name]['history']) > 20: 
            data['rates'][site_name]['history'].pop(0)

        # ذخیره کل فایل (با حفظ بقیه قیمت‌ها)
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ آپدیت شد: {site_name} -> {new_price_val}")

    except Exception as e:
        print(f"❌ خطا: {e}")

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    msg = event.raw_text
    # جستجو در خطوط پیام برای پیدا کردن قیمت فروش
    for site_key, telegram_key in mapping.items():
        if telegram_key in msg:
            lines = msg.split('\n')
            for line in lines:
                if "فروش" in line and any(char.isdigit() for char in line):
                    # استخراج عدد قیمت
                    price_match = re.findall(r'\d+[.,]?\d*', line)
                    if price_match:
                        await update_json_file(site_key, price_match[-1])

print("🚀 ربات با موفقیت استارت شد...")
client.start()
client.run_until_disconnected()
    
