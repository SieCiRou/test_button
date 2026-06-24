# stat.py
import os
import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# 設定 matplotlib 支援中文顯示
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體
plt.rcParams['axes.unicode_minus'] = False

def generate_report(excel_file="RF_test01_Results.xlsx", output_image="RF_Test_Report.png"):
    if not os.path.exists(excel_file):
        print(f"❌ 找不到來源 Excel 檔案: {excel_file}，無法產出統計報表。")
        return

    print(f"📊 正在讀取 {excel_file} 分析數據中...")
    
    # 讀取資料
    df = pd.read_excel(excel_file, sheet_name="測試結果")
    
    if df.empty:
        print("⚠ Excel 內無任何數據。")
        return

    # 建立一個大圖表畫布 (包含兩個子圖：1. 趨勢折線圖, 2. 每個按鈕平均耗時)
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # ------------------- 圖一：隨著測試步數推進的耗時折線圖 -------------------
    sns.lineplot(
        ax=axes[0], 
        data=df, 
        x=df.index + 1, 
        y='新鈕變色時間(ms)', 
        hue='輪次', 
        marker='o', 
        linewidth=2
    )
    axes[0].set_title('全測試流程：新鈕變色時間反應趨勢', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('測試步驟累計 (Step ID)', fontsize=11)
    axes[0].set_ylabel('反應時間 (ms)', fontsize=11)
    axes[0].grid(True, linestyle='--', alpha=0.6)

    # ------------------- 圖二：各按鈕平均耗時條形圖 (分析誰最慢) -------------------
    avg_df = df.groupby('按鈕實體ID')['新鈕變色時間(ms)'].mean().reset_index()
    # 依原本 UI 數字排序
    import re
    avg_df['num'] = avg_df['按鈕實體ID'].apply(lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)
    avg_df = avg_df.sort_values('num')

    sns.barplot(
        ax=axes[1], 
        data=avg_df, 
        x='按鈕實體ID', 
        y='新鈕變色時間(ms)', 
        palette='Blues_d'
    )
    axes[1].set_title('各按鈕平均變色反應時間 (比較效能)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('按鈕實體 ID', fontsize=11)
    axes[1].set_ylabel('平均時間 (ms)', fontsize=11)
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha='right')
    axes[1].grid(True, linestyle='--', alpha=0.4)

    # 加一個總和平均線
    global_mean = df['新鈕變色時間(ms)'].mean()
    axes[1].axhline(global_mean, color='red', linestyle=':', label=f'全體平均: {global_mean:.1f}ms')
    axes[1].legend()

    plt.tight_layout()
    
    # 儲存圖片
    plt.savefig(output_image, dpi=300)
    plt.close()
    
    print(f"🟢 統計報表生成成功！已儲存圖表至: [ {output_image} ]")

if __name__ == "__main__":
    generate_report()