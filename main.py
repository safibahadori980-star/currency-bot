import re, json, os
from telethon import TelegramClient, events

# اطلاعات پایه تلگرام
api_id = 2040 
api_hash = 'b18441a1ff62a0123094e073c68e1462'

# توکن شما که از BotFather گرفتی
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s' 

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

mapping = {
    "دالر هرات": "دالر به افغانی",
    "یورو هرات": "یورو به افغانی",
    "تومان چک": "تومان چک",
    "تومان بانکی": "تومان بانکی",
    "کلدار (پاکستان)": "کلدار افغانی"
}

@client.on(events.NewMessage)
async def handler(event):
    if event.is_private:
        msg = event.raw_text
        try:
            with open('last_rates.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated = False
            for site_key, telegram_key in mapping.items():
                if telegram_key in msg:
                    lines = msg.split('\n')
                    for line in lines:
                        if "فروش" in line:
                            price_match = re.findall(r'\d+[.,]?\d*', line)
                            if price_match:
                                new_val = price_match[-1].replace(',', '')
                                data['rates'][site_key]['current'] = "{:,}".format(int(float(new_val)))
                                updated = True
            
            if updated:
                with open('last_rates.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("✅ سایت با موفقیت آپدیت شد")
        except Exception as e:
            print(f"❌ خطا: {str(e)}")

print("🚀 ربات آماده است...")
client.run_until_disconnected()
