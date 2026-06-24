# data_stats.py 產生報表圖表與 HTML 整合頁面
import os
import re
from datetime import datetime

import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 設定 matplotlib 支援中文顯示
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體
plt.rcParams['axes.unicode_minus'] = False

def generate_report(excel_file="RF_test01_Results.xlsx"):
    # 容錯機制：優先找當天整合的 Excel 檔案
    if not os.path.exists(excel_file):
        today_str = datetime.now().strftime("%Y%m%d")
        fallback_file = f"RF_All_Tests_Results_{today_str}.xlsx"
        if os.path.exists(fallback_file):
            excel_file = fallback_file
        else:
            print(f"❌ 找不到 Excel 來源檔: {excel_file}")
            return

    time_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_image = f"RF_Report_{time_suffix}.png"
    output_html = f"RF_Report_{time_suffix}.html"

    print(f"📊 正在從 {excel_file} 讀取多重測試數據...")
    xl = pd.ExcelFile(excel_file)
    
    summary_html_blocks = ""
    fig, axes = plt.subplots(3, 1, figsize=(15, 20)) # 稍微放大畫布，利於標籤排版
    
    def get_num(x):
        nums = re.findall(r'\d+', str(x))
        return int(nums[0]) if nums else 0

    # ------------------- 1. 常規規律測試分析 -------------------
    if "常規規律測試" in xl.sheet_names:
        df1 = xl.parse("常規規律測試")
        if not df1.empty:
            # 💡 關鍵優化：依據「輪次」分組，並建立各自獨立的「步驟序號」以達成線段完美重合
            df1['步驟序號'] = df1.groupby('輪次').cumcount() + 1
            
            # 繪製重合折線圖
            sns.lineplot(ax=axes[0], data=df1, x='步驟序號', y='新鈕變色時間(ms)', hue='輪次', marker='o', linewidth=2.5, markersize=8)
            axes[0].set_title('🟢 常規規律測試：各輪次反應時間重合對比 (X軸附帶按鈕ID)', fontsize=14, fontweight='bold', pad=12)
            axes[0].set_xlabel('測試時序步驟', fontsize=11)
            axes[0].grid(True, linestyle='--', alpha=0.5)
            
            # 💡 說服力標籤：直接把按鈕名稱標註在第一輪的節點上方
            df1_cycle1 = df1[df1['輪次'].str.contains('1')]
            for _, row in df1_cycle1.iterrows():
                axes[0].text(row['步驟序號'], row['新鈕變色時間(ms)'] + 2, str(row['按鈕實體ID']), 
                             ha='center', va='bottom', fontsize=9, color='green', fontweight='bold', rotation=15)
            
            # 設定標準 X 軸刻度
            step_max = df1['步驟序號'].max()
            axes[0].set_xticks(range(1, step_max + 1))
            
            avg_time = df1['新鈕變色時間(ms)'].mean()
            axes[0].axhline(avg_time, color='red', linestyle=':', alpha=0.8, label=f'總平均線 ({avg_time:.1f} ms)')
            axes[0].legend(loc='upper right', fontsize=10)
            
            summary_html_blocks += f"""
            <div class='card' style='border-left: 5px solid #2ecc71;'>
                <h3>🟢 常規規律測試總結</h3>
                <p>總測試步數：<b>{len(df1)}</b> 步</p>
                <p>平均新鈕變色反應時間：<b style='color:#2ecc71;'>{avg_time:.2f} ms</b></p>
                <p>最大延遲點：<b>{df1['新鈕變色時間(ms)'].max():.2f} ms</b></p>
            </div>
            """
        else:
            axes[0].text(0.5, 0.5, '常規規律測試分頁數據為空', ha='center', va='center')
    else:
        axes[0].text(0.5, 0.5, '無常規規律測試數據', ha='center', va='center')

    # ------------------- 2. 特殊規律測試分析 -------------------
    if "特殊規律測試" in xl.sheet_names:
        df2 = xl.parse("特殊規律測試")
        if not df2.empty:
            # 💡 關鍵優化：依據「輪次」建立各自獨立的「步驟序號」，徹底解決特殊測試線段中斷或無標籤問題
            df2['步驟序號'] = df2.groupby('輪次').cumcount() + 1
            
            # 繪製重合折線圖
            sns.lineplot(ax=axes[1], data=df2, x='步驟序號', y='新鈕變色時間(ms)', hue='輪次', marker='s', palette='Oranges', linewidth=2.5, markersize=8)
            axes[1].set_title('🟠 特殊規律測試 (+1/-1/+2)：多輪走勢重合比對 (軌跡標註)', fontsize=14, fontweight='bold', pad=12)
            axes[1].set_xlabel('測試時序步驟', fontsize=11)
            axes[1].grid(True, linestyle='--', alpha=0.5)
            
            # 💡 說服力標籤：將特殊規律的點擊軌跡名稱標註在圖表上，讓報告極具觀察價值！
            df2_cycle1 = df2[df2['輪次'].str.contains('1')]
            for _, row in df2_cycle1.iterrows():
                axes[1].text(row['步驟序號'], row['新鈕變色時間(ms)'] + 2, str(row['按鈕實體ID']), 
                             ha='center', va='bottom', fontsize=9, color='darkorange', fontweight='bold', rotation=15)
            
            step_max2 = df2['步驟序號'].max()
            axes[1].set_xticks(range(1, step_max2 + 1))
            
            avg_time2 = df2['新鈕變色時間(ms)'].mean()
            axes[1].axhline(avg_time2, color='chocolate', linestyle=':', alpha=0.8, label=f'總平均線 ({avg_time2:.1f} ms)')
            axes[1].legend(loc='upper right', fontsize=10)
            
            summary_html_blocks += f"""
            <div class='card' style='border-left: 5px solid #e67e22;'>
                <h3>🟠 特殊規律測試總結</h3>
                <p>總測試步數：<b>{len(df2)}</b> 步</p>
                <p>平均新鈕變色反應時間：<b style='color:#e67e22;'>{avg_time2:.2f} ms</b></p>
                <p>最大延遲點：<b>{df2['新鈕變色時間(ms)'].max():.2f} ms</b></p>
            </div>
            """
        else:
            axes[1].text(0.5, 0.5, '特殊規律測試分頁數據為空', ha='center', va='center')
    else:
        axes[1].text(0.5, 0.5, '無特殊規律測試數據', ha='center', va='center')

    # ------------------- 3. 單鈕互動測試分析 (變藍 vs 變灰) -------------------
    if "單鈕互動測試" in xl.sheet_names:
        df3 = xl.parse("單鈕互動測試")
        if not df3.empty:
            df3['sort_idx'] = df3['按鈕實體ID'].apply(get_num)
            df3_grouped = df3.groupby(['按鈕實體ID', 'sort_idx'])[['變藍耗時(ms)', '變灰耗時(ms)']].mean().reset_index().sort_values('sort_idx')
            
            df_melt = df3_grouped.melt(id_vars=['按鈕實體ID'], value_vars=['變藍耗時(ms)', '變灰耗時(ms)'], var_name='狀態類型', value_name='時間(ms)')
            
            bars = sns.barplot(ax=axes[2], data=df_melt, x='按鈕實體ID', y='時間(ms)', hue='狀態類型', palette='Set2', edgecolor='black', alpha=0.85)
            axes[2].set_title('🔵 單鈕互動測試：各按鈕 [變藍(ON) vs 變灰(OFF)] 平均耗時對比', fontsize=14, fontweight='bold', pad=12)
            
            for container in axes[2].containers:
                axes[2].bar_label(container, fmt='%.1f', padding=3, fontsize=9, fontweight='bold')
            
            axes[2].set_xticks(range(len(df3_grouped)))
            axes[2].set_xticklabels(df3_grouped['按鈕實體ID'], rotation=25, ha='right', fontsize=9)
            axes[2].grid(True, linestyle='--', alpha=0.4, axis='y')
            
            summary_html_blocks += f"""
            <div class='card' style='border-left: 5px solid #3498db;'>
                <h3>🔵 單鈕自我切換測試總結</h3>
                <p>平均點擊變藍(ON)耗時：<b>{df3['變藍耗時(ms)'].mean():.2f} ms</b></p>
                <p>平均恢復變灰(OFF)耗時：<b>{df3['變灰耗時(ms)'].mean():.2f} ms</b></p>
            </div>
            """
        else:
            axes[2].text(0.5, 0.5, '單鈕互動測試分頁數據為空', ha='center', va='center')
    else:
        axes[2].text(0.5, 0.5, '無單鈕互動測試數據', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_image, dpi=200)
    plt.close()
    print(f"🟢 統計圖表成功儲存至: [ {output_image} ]")

    # ------------------- 4. 輸出動態網頁 HTML 報表 -------------------
    html_template = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>RF Switch 自動化測試整合報告</title>
        <style>
            body {{ font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px; color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-top: 0; }}
            .meta-info {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
            .dashboard {{ display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }}
            .card {{ flex: 1; min-width: 280px; background: #fff; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-radius: 4px; background-color: #fafbfc; }}
            .card h3 {{ margin-top: 0; color: #2c3e50; font-size: 1.1em; }}
            .chart-container {{ text-align: center; margin-top: 30px; }}
            .chart-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .footer {{ text-align: center; margin-top: 40px; color: #bdc3c7; font-size: 0.85em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📡 RF Switch Tool 自動化測試整合報告</h1>
            <div class="meta-info">
                <p>📊 數據來源原始檔：<b>{excel_file}</b></p>
                <p>⏱ 報告產出時間：<b>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</b></p>
            </div>
            <div class="dashboard">
                {summary_html_blocks}
            </div>
            <div class="chart-container">
                <h2>📈 數據視覺化圖表</h2>
                <img src="{output_image}" alt="測試統計圖表">
            </div>
            <div class="footer">
                RF Switch Tool 自動化測試流水線系統 • 自動生成報告
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"🎉 網頁報告成功儲存至: [ {output_html} ]")

if __name__ == "__main__":
    generate_report()