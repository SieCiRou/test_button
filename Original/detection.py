import win32gui

def show_all_active_windows():
    print("=" * 50)
    print(" 目前系統中所有可偵測到的視窗標題清單：")
    print("=" * 50)
    
    # 紀錄找到的視窗數量
    count = 0
    
    # Windows 回呼函式，用來檢查每個視窗
    def enum_windows_callback(hwnd, extra):
        nonlocal count
        # 確保視窗是顯示狀態，且有標題文字
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title.strip(): # 略過空白標題
                print(f"【標題】: {title}")
                count += 1
                
    # 呼叫 Windows API 巡覽所有視窗
    win32gui.EnumWindows(enum_windows_callback, None)
    
    print("=" * 50)
    print(f" 總共找到 {count} 個有效的視窗。")
    print(" 提示：請在上方清單中尋找您的 VB.NET 程式標題！")
    print("=" * 50)

if __name__ == "__main__":
    show_all_active_windows()
