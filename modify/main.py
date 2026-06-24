# main.py   正常/交錯切換測試
import re
import configparser
import os
from base_tester import RFTesterCore

class RFSwitchTool:
    def __init__(self, config_file="config.ini"):
        # 讀取設定檔
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"找不到設定檔 {config_file}，請先執行 inspect_tool.py 生成！")
            
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        
        title = config.get('TARGET', 'window_title')
        self.button_id_list = config.get('BUTTONS', 'id_list').split(',')
        
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
        直接從 config 載入按鈕清單，並與 UI 進行連線映射
        """
        if not self.tester.main_win:
            self.tester.connect_window()

        print(f"從設定檔載入並對照 UI 按鈕中... 共 {len(self.button_id_list)} 個")
        
        # 註冊到核心引擎
        self.tester.register_buttons(self.button_id_list)
        return len(self.button_id_list)