import re, json, os, asyncio
from telethon import TelegramClient

# این دو مقدار رسمی و عمومی هستند و نباید تغییر کنند
api_id = 6
api_hash = 'eb06d4abfb49ad3eeb1aeb98ae0f581e'

# توکن ربات خودت (درست است)
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s' 
SOURCE_CHANNEL = 'NerkhYab_Khorasan'

async def main():
    # استفاده از None برای محیط گیت‌هاب ضروری است
    client = TelegramClient(None, api_id, api_hash)
    
    print("در حال اتصال به تلگرام...")
    await client.start(bot_token=bot_token)
    
    mapping = {
        "دالر هرات": "دالر به افغانی",
        "یورو هرات": "یورو به افغانی",
        "تومان چک": "تومان چک",
        "تومان بانکی": "تومان بانکی",
        "کلدار (پاکستان)": "کلدار افغانی"
    }

    file_name = 'last_rates.json'
    
    # خواندن دیتای فعلی (که دستی وارد کردی) برای حفظ ساختار
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    updated = False
    print("در حال دریافت پیام‌ها...")
    async for message in client.iter_messages(SOURCE_CHANNEL, limit=15):
        if message.text:
            for site_key, telegram_key in mapping.items():
                if telegram_key in message.text:
                    lines = message.text.split('\n')
                    for line in lines:
                        if "فروش" in line:
                            price_match = re.findall(r'\d+[.,]?\d*', line)
                            if price_match:
                                new_val = price_match[-1].replace(',', '')
                                # مقایسه برای تعیین وضعیت up یا down
                                if data['rates'][site_key]['current'] != "---":
                                    old_val = float(data['rates'][site_key]['current'])
                                    current_val = float(new_val)
                                    if current_val > old_val:
                                        data['rates'][site_key]['status'] = "up"
                                    elif current_val < old_val:
                                        data['rates'][site_key]['status'] = "down"
                                
                                data['rates'][site_key]['current'] = new_val
                                updated = True

    if updated:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("فایل با موفقیت آپدیت شد.")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
