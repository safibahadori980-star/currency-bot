import telethon
from telethon import TelegramClient, events
import json
import os
from datetime import datetime

# اطلاعات تلگرام خودت را اینجا بذار
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
channel_id = 'کانال_مورد_نظر' # مثلاً @nerkhyab_channel

client = TelegramClient('session', api_id, api_hash)

def update_json(name, new_price):
    file_path = 'last_rates.json'
    
    # خواندن فایل قدیمی
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"rates": {}}

    # اگر ارز از قبل نبود، بسازش
    if name not in data["rates"]:
        data["rates"][name] = {"current": "0", "status": "up", "diff": "0.0", "history": []}

    old_price_str = data["rates"][name]["current"].replace(',', '')
    new_price_str = str(new_price).replace(',', '')

    try:
        old_p = float(old_price_str)
        new_p = float(new_price_str)
        
        # محاسبه تغییرات
        if new_p > old_p:
            status = "up"
        elif new_p < old_p:
            status = "down"
        else:
            status = data["rates"][name].get("status", "up")

        diff = 0
        if old_p != 0:
            diff = round(((new_p - old_p) / old_p) * 100, 2)

        # آپدیت لیست تاریخچه (برای نمودار)
        history = data["rates"][name].get("history", [])
        history.append(new_p)
        if len(history) > 20: # فقط ۲۰ قیمت آخر را نگه دار
            history.pop(0)

        # ذخیره نهایی
        data["rates"][name] = {
            "current": "{:,}".format(int(new_p)),
            "status": status,
            "diff": str(abs(diff)),
            "history": history
        }
        data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    except:
        pass

@client.on(events.NewMessage(chats=channel_id))
async def my_event_handler(event):
    text = event.raw_text
    # اینجا باید منطق استخراج قیمت از متن پیام کانال خودت را بنویسی
    # مثلاً: اگر در پیام کلمه "دالر هرات" بود، عدد جلوی آن را بردار
    # فعلاً برای تست:
    if "دالر هرات" in text:
        # فرض کنیم پیام این شکلی است: دالر هرات 62450
        price = ''.join(filter(str.isdigit, text))
        update_json("دالر هرات", price)

client.start()
client.run_until_disconnected()
