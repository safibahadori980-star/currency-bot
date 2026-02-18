import requests
import json
import time

def get_live_rates():
    # لینک مستقیم فایل خودت در گیت‌هاب
    url = "https://raw.githubusercontent.com/Nerkhyab/app/main/last_rates.json"
    
    try:
        # جلوگیری از کش شدن (Cache) برای دریافت قیمت لحظه‌ای
        response = requests.get(f"{url}?t={int(time.time())}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            display_ui(data)
        else:
            print("❌ خطا در دریافت دیتای آنلاین")
    except Exception as e:
        print(f"⚠️ خطای اتصال: {e}")

def display_ui(data):
    rates = data.get("rates", {})
    
    print("\n" + "═"*45)
    print("        💎 نـرخ‌یاب لـحظـه‌ای هـرات 💎")
    print(f"        🕒 بـروزرسانی: {time.strftime('%H:%M:%S')}")
    print("═"*45)
    
    # چیدمان زیبا برای هر ارز
    for name, info in rates.items():
        val = info.get('current', '---')
        status = info.get('status', 'same')
        percent = info.get('percent', '0.00%')
        
        # تعیین آیکون بر اساس وضعیت نوسان شما
        if status == "up":
            arrow = "🟢 ▲"
        elif status == "down":
            arrow = "🔴 ▼"
        else:
            arrow = "⚪ ▬"
            
        # نمایش تراز شده نرخ‌ها
        print(f"{arrow} {name:<15} : {val:>8}  ({percent:>7})")
    
    print("═"*45)
    print("   🌐 منبع: کانال نرخ یاب خراسان (GitHub)")

if __name__ == "__main__":
    get_live_rates()
