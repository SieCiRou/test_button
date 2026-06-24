# inspect_tool.py
import pywinauto
from pywinauto import Desktop
import sys
import configparser
import os

sys.stdout.reconfigure(errors='replace')

def safe_print_title(title):
    try:
        clean_title = title.encode('utf-16', 'surrogatepass').decode('utf-16', 'replace')
        print(f" -> {clean_title}")
    except Exception:
        print(f" -> {title.encode('utf-8', 'ignore').decode('utf-8', 'ignore')}")

def list_all_windows():
    print("\n" + "="*30)
    print(" 🔍 目前桌面上的所有視窗標題：")
    print("="*30)
    windows = Desktop(backend="win32").windows()
    found_any = False
    for w in windows:
        title = w.window_text()
        if title:
            safe_print_title(title)
            found_any = True
    print("="*30 + "\n")

def inspect_and_generate_config(target_title, config_file="config.ini"):
    """連線視窗，抓取所有 CheckBox 按鈕並導出為 config.ini"""
    print(f"嘗試連線到視窗: [{target_title}] ...")
    try:
        app = pywinauto.Application(backend="win32").connect(title=target_title)
        window = app.window(title=target_title)
        
        print("\n🟢 連線成功！開始剖析 CheckBox 元件並建立設定檔...")
        
        all_controls = window.descendants()
        discovered_ids = []
        
        for control in all_controls:
            try:
                auto_id = control.automation_id()
                # 篩選條件：必須是可見的 CheckBox
                if auto_id and auto_id.startswith("CheckBox") and control.is_visible():
                    discovered_ids.append(auto_id)
            except Exception:
                continue
        
        discovered_ids = list(set(discovered_ids))
        
        # 排序自然數 (避免 1, 11, 2 錯亂)
        import re
        def extract_number(auto_id):
            numbers = [int(n) for n in re.findall(r'\d+', auto_id)]
            return tuple(numbers) if numbers else (0,)
        discovered_ids.sort(key=extract_number)

        if not discovered_ids:
            print("⚠ 錯誤：在該視窗內沒有偵測到任何符合條件的 CheckBox 元件！無法生成 Config。")
            return

        # 開始寫入 config.ini
        config = configparser.ConfigParser()
        config['TARGET'] = {
            'window_title': target_title
        }
        # 將按鈕清單用逗號隔開存成字串
        config['BUTTONS'] = {
            'id_list': ",".join(discovered_ids)
        }
        
        with open(config_file, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
            
        print(f"\n🎉 設定檔生成成功 -> [ {config_file} ]")
        print(f"   共紀錄了 {len(discovered_ids)} 個按鈕。")
        print(f"   按鈕清單: {discovered_ids}\n")
        
    except pywinauto.findwindows.ElementNotFoundError:
        print(f"\n❌ 錯誤：找不到視窗 [{target_title}]！請確認名稱是否正確。")

if __name__ == "__main__":
    # 1. 顯示當前視窗，供你複製
    list_all_windows()
    
    # 2. 自動偵測：你可以在這裡輸入你在上方清單看到的實際 Title 
    # (例如你上次抓到的: RF Switch Tool V3.0_build_2605191621)
    CURRENT_SOFTWARE_TITLE = "RF Switch Tool V1.2_build_2512111636" 
    
    inspect_and_generate_config(CURRENT_SOFTWARE_TITLE)