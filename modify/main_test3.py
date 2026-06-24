# main_test3.py 單鈕自我 ON/OFF 測試
import time
from datetime import datetime
from main import RFSwitchTool

def run_btn_test(total_cycles=2, excel_file="RF_test03_Results.xlsx"):
    # 初始化並自動探索 UI 上的所有按鈕
    tool = RFSwitchTool()
    total_btns = tool.auto_discover_buttons()

    print(f"\n[單鈕自我切換測試] 偵測到 {total_btns} 個按鈕。將執行 {total_cycles} 輪測試。")

    for cycle in range(1, total_cycles + 1):
        print(f"\n--- [單鈕測試] 第 {cycle} 輪測試開始 ---")
        
        # 測試每一個按鈕
        for idx in range(total_btns):
            btn_info = tool.tester.buttons[idx]
            curr_id_name = btn_info["id_name"]
            human_num = idx + 1  # 人類直覺編號 (1開始)
            
            print(f"\n  👉 開始測試按鈕 {human_num} ({curr_id_name})")

            # ==========================================
            # 階段一：從 OFF (灰) 點擊變成 ON (藍)
            # ==========================================
            tool.tester.main_win.set_focus()
            btn_info["obj"].click_input()
            t0 = time.perf_counter()
            
            t_on = None
            while (time.perf_counter() - t0) < 2.3:  # 逾時設定
                now = time.perf_counter()
                # 掃描多點，只要有任一點變藍即代表 ON 成功
                for px, py in btn_info["points"]:
                    if tool.tester._is_steel_blue(tool.tester._get_pixel_color(tool.tester.hdc, px, py)):
                        t_on = now
                        break
                if t_on:
                    break

            res_on = (t_on - t0) * 1000 if t_on else 0
            status_on = "成功" if t_on else "逾時"
            print(f"    [OFF -> ON ] {status_on}: {res_on:.1f}ms")
            
            # 等待切換穩定
            time.sleep(1) 

            # ==========================================
            # 階段二：從 ON (藍) 再點擊變回 OFF (灰)
            # ==========================================
            btn_info["obj"].click_input()
            t1 = time.perf_counter()
            
            t_off = None
            while (time.perf_counter() - t1) < 2.3:
                now = time.perf_counter()
                # 掃描多點，只要有任一點變回灰色即代表 OFF 成功
                for px, py in btn_info["points"]:
                    if tool.tester._is_slate_gray(tool.tester._get_pixel_color(tool.tester.hdc, px, py)):
                        t_off = now
                        break
                if t_off:
                    break

            res_off = (t_off - t1) * 1000 if t_off else 0
            status_off = "成功" if t_off else "逾時"
            print(f"    [ON  -> OFF] {status_off}: {res_off:.1f}ms")

            # ==========================================
            # 階段三：紀錄數據至 Excel
            # ==========================================
            # 重新整理欄位以符合單鈕測試的需求
            record_row = [
                f"第 {cycle} 輪", 
                f"按鈕 {human_num}", 
                curr_id_name, 
                round(res_on, 2),   # 變藍耗時
                round(res_off, 2),  # 變灰耗時
                round(res_on + res_off, 2) # 單鈕總互動耗時
                ,datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 測試時間
            ]
            
            # 這裡微調一下寫入的 Header 辨識度
            tool.tester.log_to_excel(excel_file, cycle, record_row)
            
            # 每個按鈕測試完畢後稍微暫停，再換下一個按鈕
            time.sleep(1.2)
    tool.tester.close()
    print(f"\n單鈕自我切換測試完成！ 結果已存至 {excel_file}")

if __name__ == "__main__":    # 執行此檔案，測試所有按鈕的自我切換功能，預設 2 輪
    run_btn_test(total_cycles=5)