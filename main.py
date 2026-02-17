import re
import json
import os
import asyncio
from telethon import TelegramClient

# --- تنظیمات اتصال ---
api_id = 2040 
api_hash = 'b18441a1ff62a0123094e073c68e1462'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s' 
SOURCE_CHANNEL = '@NerkhYab_Khorasan' 

# استفاده از None باعث می‌شود فایل سشن ساخته نشود و مشکل لاگین گیت‌هاب حل شود
client = TelegramClient(None, api_id, api_hash)

# نقشه‌برداری نام‌ها (از تلگرام به سایت شما)
mapping = {
    "دالر هرات": "دالر به افغانی",
    "یورو هرات": "یورو به افغانی",
    "تومان چک": "تومان چک",
    "تومان بانکی": "تومان بانکی",
    "کلدار (پاکستان)": "کلدار افغانی"
}

async def main():
    print("🚀 در حال اتصال به تلگرام...")
    await client.start(bot_token=bot_token)
    
    file_name = 'last_rates.json'
    
    # لود کردن دیتای قبلی برای محاسبه تغییرات (فلش سبز و قرمز)
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"rates": {}}
    else:
        data = {"rates": {}}

    # پیش‌فرض سازی اگر دیتایی نبود
    for key in mapping.keys():
        if key not in data["rates"]:
            data["rates"][key] = {"current": "---", "status": "up", "diff": "0.00"}

    updated = False
    print(f"📥 در حال بررسی پیام‌های کانال {SOURCE_CHANNEL}...")
    
    async for message in client.iter_messages(SOURCE_CHANNEL, limit=20):
        if not message.text:
            continue
        
        text = message.text
        for site_key, telegram_key in mapping.items():
            if telegram_key in text:
                lines = text.split('\n')
                for line in lines:
                    if "فروش" in line:
                        # استخراج عدد (مثلاً از ۶۲.۴۵ یا ۶۲,۴۵۰)
                        price_match = re.findall(r'\d+[.,]?\d*', line)
                        if price_match:
                            new_val = price_match[-1].replace(',', '')
                            
                            # محاسبه درصد تغییر برای نمایش فلش‌ها در ظاهر سایت
                            try:
                                old_val = data['rates'][site_key]['current'].replace(',', '')
                                if old_val != "---" and old_val != new_val:
                                    diff = round(((float(new_val) - float(old_val)) / float(old_val)) * 100, 2)
                                    data['rates'][site_key]['status'] = "up" if diff >= 0 else "down"
                                    data['rates'][site_key]['diff'] = str(abs(diff))
                            except:
                                pass
                            
                            data['rates'][site_key]['current'] = new_val
                            updated = True
                            print(f"✅ بروزرسانی {site_key}: {new_val}")

    if updated:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("💾 فایل last_rates.json با موفقیت ذخیره شد.")
    else:
        print("⚠️ هیچ نرخ جدیدی پیدا نشد. متن پیام‌های کانال را چک کنید.")

# اجرای اصلی
if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
