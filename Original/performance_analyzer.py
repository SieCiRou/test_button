import os
import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class FlexiblePerformanceAnalyzer:
    """可動態指定欄位與標籤的物件化效能對比分析器"""
    
    def __init__(self, file_a: str, label_a: str, file_b: str, label_b: str, target_column: str):
        self.file_a = file_a
        self.label_a = label_a
        self.file_b = file_b
        self.label_b = label_b
        self.target_column = target_column
        
        self.df_a = None
        self.df_b = None
        self.stats_summary = {}

    def load_and_clean_data(self):
        """讀取檔案並動態清洗指定欄位"""
        try:
            self.df_a = pd.read_excel(self.file_a)
            self.df_b = pd.read_excel(self.file_b)
            
            # 檢查欄位是否存在
            if self.target_column not in self.df_a.columns or self.target_column not in self.df_b.columns:
                raise KeyError(f"在 Excel 中找不到您指定的欄位：『{self.target_column}』，請檢查大小寫或空格。")
            
            # 清洗數據：過濾小於等於 0 的異常值與空值
            self.df_a = self.df_a[self.df_a[self.target_column] > 0].dropna(subset=[self.target_column])
            self.df_b = self.df_b[self.df_b[self.target_column] > 0].dropna(subset=[self.target_column])
            
            print(f"數據載入成功！[{self.label_a}] 有效樣本：{len(self.df_a)}筆 | [{self.label_b}] 有效樣本：{len(self.df_b)}筆")
        except Exception as e:
            raise ValueError(f"資料讀取或清洗失敗: {e}")

    def _calculate_metrics(self, data: pd.Series) -> dict:
        """計算單組數據的關鍵統計值"""
        return {
            "mean": data.mean(),
            "median": data.median(),
            "p95": np.percentile(data, 95),
            "p99": np.percentile(data, 99),
            "max": data.max(),
            "min": data.min(),
            "stdev": data.std(),
            "count": len(data)
        }

    def run_analysis(self):
        """執行統計與顯著性檢定"""
        if self.df_a is None or self.df_b is None:
            self.load_and_clean_data()
            
        data_a = self.df_a[self.target_column]
        data_b = self.df_b[self.target_column]
        
        self.stats_summary['A'] = self._calculate_metrics(data_a)
        self.stats_summary['B'] = self._calculate_metrics(data_b)
        
        # 計算差異幅度 (A相較於B，正數代表A比B大，負數代表A比B小)
        diff_pct = ((self.stats_summary['B']['mean'] - self.stats_summary['A']['mean']) / self.stats_summary['A']['mean']) * -100
        self.stats_summary['diff_pct'] = diff_pct
        
        # Welch's t-test 雙樣本檢定
        t_stat, p_value = stats.ttest_ind(data_a, data_b, equal_var=False)
        self.stats_summary['p_value'] = p_value
        self.stats_summary['is_significant'] = "是" if p_value < 0.05 else "否"

    def generate_dashboard(self, output_filename: str = "comprehensive_dashboard.html"):
        """繪製圖表與備註解讀欄，並輸出為 HTML Dashboard"""
        if not self.stats_summary:
            self.run_analysis()
            
        sa = self.stats_summary['A']
        sb = self.stats_summary['B']
        col = self.target_column
        
        # 1. 初始化 2x2 多圖表佈局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(f'{col} - 數據分佈密集度 (Box Plot)', f'關鍵統計數值橫向對比', '按鈕編號平均數值對比', '測試輪次趨勢變化'),
            specs=[[{"type": "xy"}, {"type": "bar"}], [{"type": "bar"}, {"type": "xy"}]]
        )
        
        # 圖1: 盒鬚圖
        fig.add_trace(go.Box(y=self.df_a[col], name=self.label_a, marker_color='#1f77b4'), row=1, col=1)
        fig.add_trace(go.Box(y=self.df_b[col], name=self.label_b, marker_color='#2ca02c'), row=1, col=1)
        
        # 圖2: 關鍵指標長條圖
        metrics = ['平均值', '中位數(P50)', 'P95', 'P99']
        fig.add_trace(go.Bar(x=metrics, y=[sa['mean'], sa['median'], sa['p95'], sa['p99']], name=self.label_a, marker_color='#1f77b4'), row=1, col=2)
        fig.add_trace(go.Bar(x=metrics, y=[sb['mean'], sb['median'], sb['p95'], sb['p99']], name=self.label_b, marker_color='#2ca02c'), row=1, col=2)
        
        # 圖3: 按鈕別對比 (若Excel有此欄位則繪製，無則跳過)
        if '按鈕編號' in self.df_a.columns:
            grp_a = self.df_a.groupby('按鈕編號')[col].mean().reset_index()
            grp_b = self.df_b.groupby('按鈕編號')[col].mean().reset_index()
            fig.add_trace(go.Bar(x=grp_a['按鈕編號'], y=grp_a[col], name=self.label_a, marker_color='#1f77b4', showlegend=False), row=2, col=1)
            fig.add_trace(go.Bar(x=grp_b['按鈕編號'], y=grp_b[col], name=self.label_b, marker_color='#2ca02c', showlegend=False), row=2, col=1)
            
        # 圖4: 輪次趨勢變化 (若Excel有此欄位則繪製，無則跳過)
        if '輪次' in self.df_a.columns:
            t_a = self.df_a.groupby('輪次')[col].mean().reset_index()
            t_b = self.df_b.groupby('輪次')[col].mean().reset_index()
            fig.add_trace(go.Scatter(x=t_a['輪次'], y=t_a[col], name=self.label_a, mode='lines+markers', line=dict(color='#1f77b4')), row=2, col=2)
            fig.add_trace(go.Scatter(x=t_b['輪次'], y=t_b[col], name=self.label_b, mode='lines+markers', line=dict(color='#2ca02c')), row=2, col=2)

        fig.update_layout(height=750, template="plotly_white", margin=dict(t=40, b=40, l=50, r=50))
        
        # 2. 建立頁首 KPI 區塊
        status_color = "#2ca02c" if self.stats_summary['diff_pct'] > 0 else "#d62728"
        status_text = "效率提升" if self.stats_summary['diff_pct'] > 0 else "效率下降"
        
        header_html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 25px; background-color: #fdfdfd; border-bottom: 3px solid #eef2f5;">
            <h2 style="color: #2c3e50; margin: 0 0 10px 0;">多維度數據效能對比 Dashboard</h2>
            <p style="color: #7f8c8d; margin: 0; font-size:14px;">對比欄位：<strong style="color:#333;">{col}</strong> | 基準組：{self.label_a} 🆚 對比組：{self.label_b}</p>
            
            <div style="display: flex; gap: 20px; margin-top: 20px;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; flex: 1; text-align: center; border-left: 5px solid #1f77b4;">
                    <span style="color: #666; font-size: 13px;">[{self.label_a}] 平均值</span>
                    <h3 style="margin: 8px 0; color: #1f77b4;">{sa['mean']:.2f}</h3>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; flex: 1; text-align: center; border-left: 5px solid #2ca02c;">
                    <span style="color: #666; font-size: 13px;">[{self.label_b}] 平均值</span>
                    <h3 style="margin: 8px 0; color: #2ca02c;">{sb['mean']:.2f}</h3>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; flex: 1; text-align: center; border: 1px solid {status_color};">
                    <span style="color: #666; font-size: 13px;">相對數據差異</span>
                    <h3 style="margin: 8px 0; color: {status_color};">{abs(self.stats_summary['diff_pct']):.2f}%</h3>
                    <span style="font-size: 11px; color: {status_color}; font-weight: bold;">({status_text})</span>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; flex: 1; text-align: center; border-left: 5px solid #9467bd;">
                    <span style="color: #666; font-size: 13px;">統計顯著性 (P-Value)</span>
                    <h3 style="margin: 8px 0; color: #9467bd;">{self.stats_summary['p_value']:.4e}</h3>
                    <span style="font-size: 11px; color: #27ae60 if self.stats_summary['is_significant']=='是' else '#c0392b'">
                        具備顯著差異：<b>{self.stats_summary['is_significant']}</b>
                    </span>
                </div>
            </div>
        </div>
        """
        
        # 3. 建立詳細的【統計數值差異與解讀備註欄】
        notes_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 25px; background-color: #ffffff; margin-top: 20px;">
            <div style="border-top: 2px solid #dee2e6; padding-top: 15px;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">📝 統計數值對照表與深入解讀備註</h3>
                <table style="width: 100%; border-collapse: collapse; text-align: left; margin-bottom: 20px; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #f1f3f5;">
                            <th style="padding: 10px; border: 1px solid #dee2e6;">統計統計指標</th>
                            <th style="padding: 10px; border: 1px solid #dee2e6;">{self.label_a} (基準)</th>
                            <th style="padding: 10px; border: 1px solid #dee2e6;">{self.label_b} (對比)</th>
                            <th style="padding: 10px; border: 1px solid #dee2e6; width: 65%;">💡 數據差異能看出哪些指標含意？（備註說明）</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">平均值 (Mean)</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{sa['mean']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{sb['mean']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; color: #555;">
                                <b>代表整體的「平均表現」。</b><br>
                                如果 [{self.label_b}] 低於 [{self.label_a}]，代表新版程式碼在巨觀上成功縮短了整體的處理時間。
                            </td>
                        </tr>
                        <tr style="background-color: #fafafa;">
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">中位數 (Median/P50)</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{sa['median']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{sb['median']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; color: #555;">
                                <b>代表最普羅大眾、最典型的使用者體驗。</b><br>
                                中位數不受極端卡頓值影響。如果平均值和中位數很接近，說明資料分佈對稱；若平均值遠大於中位數，說明該版本存在嚴重的極端卡頓情況。
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">第 95 / 99 百分位數<br>(P95 / P99)</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">P95: {sa['p95']:.2f}<br>P99: {sa['p99']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">P95: {sb['p95']:.2f}<br>P99: {sb['p99']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; color: #555;">
                                <b>用來檢視「最壞的 5% 與 1% 使用者會有多卡頓」。</b><br>
                                這在軟體工程中是極為關鍵的長尾指標（Tail Latency）。若 [{self.label_b}] 的 P99 顯著下降，代表重構成功消除了底層突發性的死鎖、記憶體阻塞或重繪（Repaint）帶來的嚴重 UI 凍結。
                            </td>
                        </tr>
                        <tr style="background-color: #fafafa;">
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">標準差 (Standard Deviation)</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{sa['stdev']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{sb['stdev']:.2f}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; color: #555;">
                                <b>代表數據的「穩定度與可預測性」。</b><br>
                                標準差越小，意味著每次點擊按鈕的變色速度越整齊。如果重構後的標準差大幅降低，說明系統執行環境變得高度穩定，消除了隨機抖動（Jitter）。
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">統計顯著性 (P-Value)</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;" colspan="2">當前計算結果 P 值為：<b>{self.stats_summary['p_value']:.4e}</b></td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; color: #555;">
                                <b>用科學方法驗證「這份進步是真有其事，還是只是隨機運氣」。</b><br>
                                當 P < 0.05（顯著性成立）時，代表我們有超過 95% 的信心可以確定 [{self.label_b}] 表現勝過 [{self.label_a}] 是因為你的程式碼寫得更好，完全排除了測試硬體暫時性變快等隨機干擾因素。
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        # 4. 寫出網頁
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(header_html)
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write(notes_html)
            
        print(f"Dashboard 已生成！請至以下路徑打開 HTML 檔案：\n {os.path.abspath(output_filename)}")

# ==========================================
# 執行入口
# ==========================================
if __name__ == "__main__":
    print("====== 泛用型動態資料對比 Dashboard 生成器 ======")
    
    # 1. 互動式輸入
    file_1 = input("1. 請輸入第一個 Excel 檔名 (如 before.xlsx): ").strip()
    name_1 = input("   └─ 請為第一個檔案自訂標籤 (如 重構前/舊代碼): ").strip() or "組別A"
    
    file_2 = input("2. 請輸入第二個 Excel 檔名 (如 after.xlsx): ").strip()
    name_2 = input("   └─ 請為第二個檔案自訂標籤 (如 重構後/新架構): ").strip() or "組別B"
    
    col_target = input("3. 請輸入欲分析的關鍵數據欄位名稱 (如 總耗時(ms)): ").strip()

    # 2. 實例化物件並執行
    analyzer = FlexiblePerformanceAnalyzer(
        file_a=file_1, label_a=name_1, 
        file_b=file_2, label_b=name_2, 
        target_column=col_target
    )
    
    analyzer.run_analysis()
    analyzer.generate_dashboard("interactive_performance_dashboard.html")
