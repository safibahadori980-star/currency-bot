import re, json, os, asyncio
from telethon import TelegramClient

# این مقادیر الان تست شده و سالم هستند
api_id = 6
api_hash = 'eb06d4abfb49ad3eeb1aeb98ae0f581e'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s'
SOURCE_CHANNEL = 'NerkhYab_Khorasan'

async def main():
    # استفاده از None برای جلوگیری از تداخل سشن در گیت‌هاب
    client = TelegramClient(None, api_id, api_hash)
    
    print("در حال اتصال به تلگرام...")
    await client.start(bot_token=bot_token)
    
    # مپینگ دقیق بر اساس متن پیام‌های کانال شما
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار افغانی": "هرات کلدار افغانی"
    }

    file_name = 'last_rates.json'
    
    # لود کردن دیتای موجود یا ساخت دیتای جدید
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    updated = False
    print("در حال دریافت آخرین پیام‌ها...")
    async for message in client.iter_messages(SOURCE_CHANNEL, limit=20):
        if message.text:
            for site_key, telegram_key in mapping.items():
                if telegram_key in message.text:
                    lines = message.text.split('\n')
                    for line in lines:
                        if "فروش" in line:
                            price_match = re.findall(r'\d+[.,]?\d*', line)
                            if price_match:
                                new_val = price_match[-1].replace(',', '')
                                # محاسبه وضعیت صعودی/نزولی
                                try:
                                    old = float(data['rates'][site_key]['current'])
                                    new = float(new_val)
                                    data['rates'][site_key]['status'] = "up" if new >= old else "down"
                                except: pass
                                
                                data['rates'][site_key]['current'] = new_val
                                updated = True

    if updated:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("نرخ‌ها با موفقیت به‌روزرسانی شدند!")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
