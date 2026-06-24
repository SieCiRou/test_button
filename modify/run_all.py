# run_all.py
import os
import sys
from datetime import datetime
import subprocess

import main_test
import main_test2
import main_test3
from data_stats import generate_report

def main():
    print("==================================================")
    print("======  RF 開關自動化測試與視覺化整合系統啟動  ======")
    print("==================================================")
    
    CONFIG_FILE = "config.ini"

    today_str = datetime.now().strftime("%Y%m%d")
    EXCEL_OUTPUT = f"RF_All_Tests_Results_{today_str}.xlsx"
    REPORT_IMAGE = f"RF_Test_Report_{today_str}.png"
    
    # 1. 檢查 Config 是否存在
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 找不到 {CONFIG_FILE}！")
        print("💡 請先單獨執行 [ inspect_tool.py ] 生成設定檔。")
        sys.exit(1)
        
    print(f"1. 成功偵測到設定檔 {CONFIG_FILE}，準備進入測試...")
    
    # 如果舊的 Excel 報表存在，先移除或提示，避免新舊數據混雜
    if os.path.exists(EXCEL_OUTPUT):
        try:
            os.remove(EXCEL_OUTPUT)
        except Exception:
            print(f"❌ 錯誤：無法清理舊的 {EXCEL_OUTPUT}，請確認該 Excel 是否被開啟中。")
            sys.exit(1)

    # 2. 執行測試 1：常規規律測試
    print("\n[RUN 1/3] ⚙ 開始執行常規規律測試 (main_test.py)...")
    try:
        main_test.run_dynamic_test(pattern_type="normal", total_cycles=2, excel_file=EXCEL_OUTPUT)
        print("🟢 常規規律測試完成。")
    except Exception as e:
        print(f"⚠ 常規測試異常中斷: {e}")

    # 3. 執行測試 2：特殊規律測試
    print("\n[RUN 2/3] ⚙ 開始執行特殊規律測試 (main_test2.py)...")
    try:
        main_test2.run_dynamic_pattern_test(total_cycles=2, excel_file=EXCEL_OUTPUT)
        print("🟢 特殊規律測試完成。")
    except Exception as e:
        print(f"⚠ 特殊規律測試異常中斷: {e}")

    # 4. 執行測試 3：單鈕自我切換測試
    print("\n[RUN 3/3] ⚙ 開始執行單鈕獨立切換測試 (main_test3.py)...")
    try:
        main_test3.run_btn_test(total_cycles=2, excel_file=EXCEL_OUTPUT)
        print("🟢 單鈕互動測試完成。")
    except Exception as e:
        print(f"⚠ 單鈕測試異常中斷: {e}")

    # 5. 整合分析與多功能報表輸出
    print("\n==================================================")
    print("📈 所有切換測試完畢！開始編譯視覺化圖表與網頁報告...")
    print("==================================================")
    
    try:
        generate_report(excel_file=EXCEL_OUTPUT)
    except Exception as e:
        print(f"❌ 產生報表失敗: {e}")
        sys.exit(1)

    print("\n==================================================")
    print(" 一鍵自動化測試流程全部結束！")
    print(f"   - 數據報表: {EXCEL_OUTPUT}")
    print("==================================================")

if __name__ == "__main__":
    main()