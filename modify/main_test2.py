# test_dynamic_pattern.py
import time
from main import RFSwitchTool

def generate_plus1_minus1_plus2_sequence(total_btns):
    """
    動態生成 (+1, -1, +2) 的全按鈕覆蓋序列
    0 -> 1 -> 0 -> 2 -> 3 -> 2 -> 4 -> 5 -> 4 -> 6 -> 7 -> 6
    """
    seq = []
    curr = 0
    
    while curr < total_btns:
        # 步驟 1: +1
        seq.append(curr)
        
        # 步驟 2: 如果還有下一個按鈕，前進到下一個再退回 (-1)
        if curr + 1 < total_btns:
            seq.append(curr + 1)
            seq.append(curr)
            
        # 步驟 3: 準備進入下一個循環 (+2)
        curr += 2
        
    return seq

def run_dynamic_pattern_test(total_cycles=2, excel_file="RF_test02_Results.xlsx"):
    # 1. 初始化工具並自動探索 UI 上的所有按鈕
    tool = RFSwitchTool()
    total_btns = tool.auto_discover_buttons()
    
    if total_btns < 2:
        print(f"錯誤：偵測到的按鈕總數為 {total_btns}，無法執行切換測試。")
        tool.tester.close()
        return

    # 2. 自動生成符合該型號按鈕總數的特殊測試序列
    test_sequence = generate_plus1_minus1_plus2_sequence(total_btns)
    
    # 將邏輯索引 (0 開始) 轉回人類直覺的按鈕編號 (1 開始) 供 Log 顯示
    human_sequence = [idx + 1 for idx in test_sequence]
    
    print(f"\n[動態生成成功]")
    print(f"實體按鈕測試順序: {human_sequence}")
    print(f"邏輯索引測試順序: {test_sequence}")

    # 初始狀態設定（先點擊序列中的最後一個按鈕，確保第一步有前按鈕可恢復）
    last_idx = test_sequence[-1]
    tool.tester.buttons[last_idx]["obj"].click_input()
    print(f"已初始化：預先點擊序列最後一個按鈕 ({tool.tester.buttons[last_idx]['id_name']})")
    time.sleep(1)

    # 執行多輪測試 (預設為 2 輪)
    for cycle in range(1, total_cycles + 1):
        print(f"\n--- [動態規律] 第 {cycle} 輪測試開始 ---")
        
        for i, curr_idx in enumerate(test_sequence):
            # 自動閉環：前一個按鈕永遠是序列中的前一格
            prev_idx = test_sequence[i - 1]
            
            curr_id_name = tool.tester.buttons[curr_idx]["id_name"]
            prev_id_name = tool.tester.buttons[prev_idx]["id_name"]
            
            # 執行時間量測
            res_prev, res_curr = tool.tester.measure_switch(curr_idx, prev_idx)
            
            status = "成功" if res_curr > 0 else "逾時"
            print(f"  [步驟 {i+1}] 切換至 {curr_id_name} (前鈕 {prev_id_name}) -> {status}: {res_curr:.1f}ms")
            
            # 寫入 Excel 報表
            record_row = [
                f"第 {cycle} 輪", 
                f"第 {i+1} 步 (鈕 {human_sequence[i]})", 
                curr_id_name, 
                round(res_prev, 2), 
                round(res_curr, 2), 
                round(res_curr, 2)
            ]
            tool.tester.log_to_excel(excel_file, cycle, record_row)
            
            time.sleep(1)

    # 釋放 Win32 資源
    tool.tester.close()
    print(f"\n測試完成！結果已儲存至 {excel_file}")

if __name__ == "__main__":
    # 測試所有按鈕 2 輪
    run_dynamic_pattern_test(total_cycles=2)