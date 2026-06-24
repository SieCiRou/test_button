# main_test3.py 單鈕自我 ON/OFF 測試
import time
from datetime import datetime
from main import RFSwitchTool

def run_btn_test(total_cycles=2, excel_file="RF_test03_Results.xlsx"):
    tool = RFSwitchTool()
    total_btns = tool.auto_discover_buttons()

    print(f"\n[單鈕自我切換測試] 偵測到 {total_btns} 個按鈕。將執行 {total_cycles} 輪測試。")

    for cycle in range(1, total_cycles + 1):
        print(f"\n--- [單鈕測試] 第 {cycle} 輪測試開始 ---")
        
        for idx in range(total_btns):
            btn_info = tool.tester.buttons[idx]
            curr_id_name = btn_info["id_name"]
            human_num = idx + 1
            
            print(f"\n  👉 開始測試按鈕 {human_num} ({curr_id_name})")

            tool.tester.main_win.set_focus()
            btn_info["obj"].click_input()
            t0 = time.perf_counter()
            
            t_on = None
            while (time.perf_counter() - t0) < 2.3:
                now = time.perf_counter()
                for px, py in btn_info["points"]:
                    if tool.tester._is_steel_blue(tool.tester._get_pixel_color(tool.tester.hdc, px, py)):
                        t_on = now
                        break
                if t_on:
                    break

            res_on = (t_on - t0) * 1000 if t_on else 0
            print(f"    [OFF -> ON ] 成功: {res_on:.1f}ms")
            time.sleep(1) 

            btn_info["obj"].click_input()
            t1 = time.perf_counter()
            
            t_off = None
            while (time.perf_counter() - t1) < 2.3:
                now = time.perf_counter()
                for px, py in btn_info["points"]:
                    if tool.tester._is_slate_gray(tool.tester._get_pixel_color(tool.tester.hdc, px, py)):
                        t_off = now
                        break
                if t_off:
                    break

            res_off = (t_off - t1) * 1000 if t_off else 0
            print(f"    [ON  -> OFF] 成功: {res_off:.1f}ms")

            current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 💡 核心修正點 1：包含 7 欄位格式，與 base_tester 頭尾完全對齊
            record_row = [
                f"第 {cycle} 輪", 
                f"按鈕 {human_num}", 
                curr_id_name, 
                round(res_on, 2),   
                round(res_off, 2),  
                round(res_on + res_off, 2),
                current_time_str
            ]
            
            # 💡 核心修正點 2：顯式指定寫入 單鈕互動測試 分頁
            tool.tester.log_to_excel(excel_file, cycle, record_row, sheet_name="單鈕互動測試")
            time.sleep(1.2)
            
    tool.tester.close()

if __name__ == "__main__":
    run_btn_test(total_cycles=2)