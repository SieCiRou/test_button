# main_test.py
import time
from main import RFSwitchTool

def run_dynamic_test(pattern_type="normal", total_cycles=2, excel_file="RF_test01_Results.xlsx"):
    # 1. 初始化工具
    tool = RFSwitchTool()
    
    # 2. 讓工具自己去畫面抓按鈕並排序，回傳總按鈕數
    total_btns = tool.auto_discover_buttons()
    
    # 3. 決定測試的邏輯順序
    if pattern_type == "normal":
        test_sequence = list(range(total_btns))
    elif pattern_type == "plus_2":
        test_sequence = [i for i in range(total_btns) if i % 2 == 0] + [i for i in range(total_btns) if i % 2 != 0]
    else:
        test_sequence = list(range(total_btns))

    print(f"產生的測試邏輯順序: {test_sequence}")

    # 4. 初始狀態（先點擊序列中的最後一個按鈕）
    last_idx = test_sequence[-1]
    tool.tester.buttons[last_idx]["obj"].click_input()
    time.sleep(1)

    # 5. 開始循環測試
    for cycle in range(1, total_cycles + 1):
        print(f"\n--- 第 {cycle} 輪測試 ---")
        for i, curr_idx in enumerate(test_sequence):
            prev_idx = test_sequence[i - 1]
            curr_id_name = tool.tester.buttons[curr_idx]["id_name"]
            
            # 量測時間
            res_prev, res_curr = tool.tester.measure_switch(curr_idx, prev_idx)
            
            status = "成功" if res_curr > 0 else "逾時"
            print(f"  [步驟 {i+1}] 目前按鈕 ({curr_id_name}) -> {status}: {res_curr:.1f}ms")
            
            # 寫入 Excel
            record_row = [f"第 {cycle} 輪", f"第 {i+1} 步", curr_id_name, round(res_prev, 2), round(res_curr, 2), round(res_curr, 2)]
            tool.tester.log_to_excel(excel_file, cycle, record_row)
            
            time.sleep(1)

    tool.tester.close()

if __name__ == "__main__":
    # 不管現在畫面上打開的是哪一個型號的軟體，直接執行就對了！
    run_dynamic_test(pattern_type="normal", total_cycles=2)