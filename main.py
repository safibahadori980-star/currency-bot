import re, json, os, asyncio
from telethon import TelegramClient

# اطلاعات اتصال
api_id = 2040 
api_hash = 'b18441a1ff62a0123094e073c68e1462'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s' 
SOURCE_CHANNEL = 'NerkhYab_Khorasan'

async def main():
    # اتصال بدون سشن برای جلوگیری از ارور شماره تلفن
    client = TelegramClient(None, api_id, api_hash)
    print("Connecting...")
    await client.start(bot_token=bot_token)
    
    mapping = {
        "دالر هرات": "دالر به افغانی",
        "یورو هرات": "یورو به افغانی",
        "تومان چک": "تومان چک",
        "تومان بانکی": "تومان بانکی",
        "کلدار (پاکستان)": "کلدار افغانی"
    }

    file_name = 'last_rates.json'
    
    # ایجاد دیتای اولیه اگر فایل وجود نداشت
    data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    # اگر فایل وجود داشت، آن را بخوان
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            print("Creating new data structure...")

    updated = False
    print("Fetching rates...")
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

    # ذخیره فایل (حتی اگر آپدیت نشد، فایل را بساز تا ارور ندهد)
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("Success! File saved.")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
