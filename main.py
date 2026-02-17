import re, json, os, asyncio
from telethon import TelegramClient

# تنظیمات اتصال
api_id = 2040 
api_hash = 'b18441a1ff62a0123094e073c68e1462'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s' 

client = TelegramClient('bot_session', api_id, api_hash)

mapping = {
    "دالر هرات": "دالر به افغانی",
    "یورو هرات": "یورو به افغانی",
    "تومان چک": "تومان چک",
    "تومان بانکی": "تومان بانکی",
    "کلدار (پاکستان)": "کلدار افغانی"
}

async def main():
    await client.start(bot_token=bot_token)
    file_name = 'last_rates.json'
    
    # ساخت یا لود کردن فایل
    if not os.path.exists(file_name):
        data = {"rates": {k: {"current": "0", "status": "up", "diff": "0.0"} for k in mapping.keys()}}
    else:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)

    updated = False
    # اسکن پیام‌های فوروارد شده به ربات
    async for message in client.iter_messages('me', limit=10):
        if not message.text: continue
        msg = message.text
        for site_key, telegram_key in mapping.items():
            if telegram_key in msg:
                lines = msg.split('\n')
                for line in lines:
                    if "فروش" in line or "خرید" in line:
                        price_match = re.findall(r'\d+[.,]?\d*', line)
                        if price_match:
                            # گرفتن آخرین عدد (قیمت فروش)
                            new_val = price_match[-1].replace(',', '')
                            data['rates'][site_key]['current'] = new_val
                            updated = True

    if updated:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ انجام شد!")
    else:
        print("❌ پیامی پیدا نشد.")

with client:
    client.loop.run_until_complete(main())
