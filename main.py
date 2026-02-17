import re, json, os, asyncio
from telethon import TelegramClient

# مقادیر استاندارد طلایی (بدون تغییر)
api_id = 2496
api_hash = '8bb4597412e4dad4213e65a9a15c4013'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s'
SOURCE_CHANNEL = 'NerkhYab_Khorasan'

async def main():
    # استفاده از سشن موقت برای گیت‌هاب
    client = TelegramClient(None, api_id, api_hash)
    await client.start(bot_token=bot_token)
    
    # این لیست دقیقاً بر اساس اسکرین‌شات پیام‌های کانال تو تنظیم شده
    mapping = {
        "دالر هرات": "هرات دالر به افغانی",
        "یورو هرات": "هرات یورو به افغانی",
        "تومان چک": "هرات تومان چک",
        "تومان بانکی": "هرات تومان بانکی",
        "کلدار افغانی": "هرات کلدار افغانی"
    }

    file_name = 'last_rates.json'
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    updated = False
    async for message in client.iter_messages(SOURCE_CHANNEL, limit=15):
        if message.text:
            for site_key, telegram_key in mapping.items():
                if telegram_key in message.text:
                    lines = message.text.split('\n')
                    for line in lines:
                        # جستجوی عدد جلوی کلمه فروش
                        if "فروش" in line:
                            price_match = re.findall(r'\d+[.,]?\d*', line)
                            if price_match:
                                new_val = price_match[-1].replace(',', '')
                                # تشخیص بالا یا پایین رفتن
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
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
