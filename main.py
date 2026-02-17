import re, json, os, asyncio
from telethon import TelegramClient

# اطلاعات ثابت
api_id = 2040 
api_hash = 'b18441a1ff62a0123094e073c68e1462'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s' 

SOURCE_CHANNEL = '@NerkhYab_Khorasan' 

# ایجاد کلاینت
client = TelegramClient('bot_session', api_id, api_hash)

mapping = {
    "دالر هرات": "دالر به افغانی",
    "یورو هرات": "یورو به افغانی",
    "تومان چک": "تومان چک",
    "تومان بانکی": "تومان بانکی",
    "کلدار (پاکستان)": "کلدار افغانی"
}

async def main():
    # اصلاح اصلی: لاگین مستقیم با توکن بدون درخواست شماره
    await client.start(bot_token=bot_token)
    
    file_name = 'last_rates.json'
    
    # لود کردن دیتای فعلی
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"rates": {k: {"current": "---", "status": "up", "diff": "0.00"} for k in mapping.keys()}}

    updated = False
    # اسکن کانال
    async for message in client.iter_messages(SOURCE_CHANNEL, limit=15):
        if not message.text: continue
        
        for site_key, telegram_key in mapping.items():
            if telegram_key in message.text:
                lines = message.text.split('\n')
                for line in lines:
                    if "فروش" in line:
                        price_match = re.findall(r'\d+[.,]?\d*', line)
                        if price_match:
                            new_val = price_match[-1].replace(',', '')
                            
                            # محاسبه تغییرات برای ظاهر جدید
                            try:
                                old_val = data['rates'][site_key]['current'].replace(',', '')
                                if old_val != "---" and old_val != new_val:
                                    diff = round(((float(new_val) - float(old_val)) / float(old_val)) * 100, 2)
                                    data['rates'][site_key]['status'] = "up" if diff >= 0 else "down"
                                    data['rates'][site_key]['diff'] = str(abs(diff))
                            except: pass
                            
                            data['rates'][site_key]['current'] = new_val
                            updated = True

    if updated:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ نرخ‌ها با موفقیت بروزرسانی شدند.")

# اجرای برنامه
with client:
    client.loop.run_until_complete(main())
