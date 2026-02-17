import re, json, os, asyncio
from telethon import TelegramClient

# اطلاعات اتصال (توکن شما تایید شد)
api_id = 6
api_hash = 'eb06d4abfb49ad3eeb1aeb98ae0f581e'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s'
SOURCE_CHANNEL = 'NerkhYab_Khorasan'

async def main():
    # استفاده از None برای جلوگیری از تداخل فایل‌های سشن در گیت‌هاب
    client = TelegramClient(None, api_id, api_hash)
    
    print("در حال اتصال به تلگرام...")
    # روش استارت اصلاح شده برای رفع ارور ApiIdInvalid
    await client.start(bot_token=bot_token)
    
    # مپینگ هماهنگ با پیام‌های کانال شما (اسکرین‌شات تلگرامت)
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار افغانی": "هرات کلدار افغانی"
    }

    file_name = 'last_rates.json'
    data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: pass

    updated = False
    print("در حال دریافت پیام‌ها...")
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
                                data['rates'][site_key]['current'] = new_val
                                updated = True

    if updated:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ نرخ‌ها با موفقیت به‌روزرسانی شدند!")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
