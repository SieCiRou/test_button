import re
from base_tester import RFTesterCore

class RFSwitchTool:
    def __init__(self, title="RF Switch Tool V3.0_build_2605191621"):
        self.tester = RFTesterCore(title)

    def _extract_number(self, auto_id):
        numbers = [int(n) for n in re.findall(r'\d+', auto_id)]
        if len(numbers) == 1:
            return (numbers[0], 0)
        elif len(numbers) >= 2:
            return (numbers[0], numbers[1])
        return (0, 0)

    def auto_discover_buttons(self):
        """
        動態框選所有可見的 CheckBox，並依名稱數字排序
        """
        if not self.tester.main_win:
            self.tester.connect_window()

        print("正在探索 UI 介面的 CheckBox...")
        
        discovered_ids = []
        
        # 1. 撈出視窗內「所有」子控制項
        all_controls = self.tester.main_win.descendants()
        
        for control in all_controls:
            try:
                # 條件：必須是可見的 (visible=True) 且 AutoID 以 'CheckBox' 開頭
                # 註：win32 後台的 control_type 通常對應 Windows 的類別名稱
                auto_id = control.automation_id()  # 取得 AutoID
                
                if auto_id and auto_id.startswith("CheckBox") and control.is_visible():
                    discovered_ids.append(auto_id)
            except Exception:
                # 某些特殊控制項可能不支援部分屬性，直接跳過即可
                continue

        # 2. 去除重複值（有時候 UI 樹狀結構會重複抓取）
        discovered_ids = list(set(discovered_ids))

        if not discovered_ids:
            raise RuntimeError("在當前視窗中找不到任何符合條件且可見的 CheckBox！")

        # 3. 依據名稱中的數字自然排序 (避免出現 1, 11, 2, 21 這種字典排序錯誤)
        discovered_ids.sort(key=self._extract_number)

        print(f"探索成功！共找到 {len(discovered_ids)} 個有效按鈕。")
        print(f"自動排序後的映射清單: {discovered_ids}")

        # 4. 註冊到核心引擎（對應到邏輯順序 0, 1, 2...）
        self.tester.register_buttons(discovered_ids)
        
        return len(discovered_ids)