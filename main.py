async def update_json_file(name, new_price_str):
    file_name = 'last_rates.json'
    try:
        # ۱. ابتدا فایل فعلی را می‌خوانیم تا قیمت‌های قبلی را داشته باشیم
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # ۲. تبدیل قیمت جدید به عدد
        new_price_val = float(new_price_str.replace(',', ''))
        
        # ۳. گرفتن قیمت قبلی از حافظه فایل
        old_price_data = data['rates'].get(name, {"current": "0"})
        old_price_str = old_price_data['current'].replace(',', '')
        old_price_val = float(old_price_str) if old_price_str != "---" else new_price_val

        # ۴. اگر قیمت جدید با قبلی فرقی نداشت، فقط زمان بروزرسانی را عوض کن
        if new_price_val == old_price_val:
            return 

        # ۵. محاسبه تغییرات و ذخیره
        status = "up" if new_price_val >= old_price_val else "down"
        diff = round(abs((new_price_val - old_price_val) / old_price_val * 100), 2) if old_price_val != 0 else 0

        data['rates'][name] = {
            "current": "{:,}".format(int(new_price_val) if new_price_val > 100 else new_price_val),
            "status": status,
            "diff": str(diff),
            "history": data['rates'][name].get('history', [])
        }
        
        # اضافه کردن به تاریخچه
        data['rates'][name]['history'].append(new_price_val)
        if len(data['rates'][name]['history']) > 20: data['rates'][name]['history'].pop(0)

        # ۶. بازنویسی فایل با حفظ بقیه ارزها
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Error updating {name}: {e}")
        
