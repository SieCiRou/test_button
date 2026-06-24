# run_all.py
import os
import sys
import subprocess
from main_test import run_dynamic_test
from data_stats import generate_report

def main():
    print("==================================================")
    print("🚀  RF 開關自動化測試與視覺化整合系統啟動  🚀")
    print("==================================================")
    
    CONFIG_FILE = "config.ini"
    EXCEL_OUTPUT = "RF_test01_Results.xlsx"
    REPORT_IMAGE = "RF_Test_Report.png"
    
    # 1. 檢查 Config 是否存在
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 找不到 {CONFIG_FILE}！")
        print("💡 請先單獨執行 [ inspect_tool.py ] 來確認你的視窗標題並產生設定檔。")
        sys.exit(1)
        
    print(f"1. 成功偵測到設定檔 {CONFIG_FILE}，準備進入測試...")
    
    # 2. 如果舊的 Excel 報表存在，先移除或提示，避免新舊數據混雜
    if os.path.exists(EXCEL_OUTPUT):
        try:
            os.remove(EXCEL_OUTPUT)
            print(f"2. 已清理上一次舊的 Excel 紀錄: {EXCEL_OUTPUT}")
        except Exception:
            print(f"⚠ 警告：無法刪除舊的 {EXCEL_OUTPUT}，請確認檔案是否被 Excel 開啟中！")
            sys.exit(1)
    else:
        print("2. 無舊報表衝突，全新測試。")

    # 3. 呼叫測試核心
    print("\n3. ⚙ 開始執行核心切換測試流程...")
    try:
        # 呼叫 main_test.py 裡的測試主函式 (測試 2 輪)
        run_dynamic_test(pattern_type="normal", total_cycles=2, excel_file=EXCEL_OUTPUT)
        print("🟢 核心切換測試順利完成！")
    except Exception as e:
        print(f"❌ 測試運作時發生嚴重錯誤: {e}")
        sys.exit(1)

    # 4. 呼叫統計報表生成
    print("\n4. 📈 測試完成，開始進行數據視覺化統計...")
    try:
        generate_report(excel_file=EXCEL_OUTPUT, output_image=REPORT_IMAGE)
        print("🟢 數據分析結束。")
    except Exception as e:
        print(f"❌ 生成報表圖形時失敗: {e}")
        sys.exit(1)

    print("\n==================================================")
    print("🎉 一鍵自動化測試流程全部結束！")
    print(f"   - 數據報表: {EXCEL_OUTPUT}")
    print(f"   - 統計圖表: {REPORT_IMAGE}")
    print("==================================================")

if __name__ == "__main__":
    main()