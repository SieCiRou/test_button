@echo off
chcp 65001 > nul
cls

set LOGFILE=run_log.txt
set IP=192.168.1.36
set PORT=5000
set VBS_FILE=telnet_runner.vbs

:: 在這裡設定每個 ss 的範圍
set num1=0
set num2=8
set num3=0
set num4=0

:: 設定總次數
set totalRuns=33

echo ================================================== >> %LOGFILE%
echo   通用自動測試  >> %LOGFILE%
echo ================================================== >> %LOGFILE%
echo.


:: 1. 動態產生 VBS 腳本
echo Set cloner = CreateObject("WScript.Shell") > %VBS_FILE% 2>> %LOGFILE%

:: 直接啟動 Windows Telnet
echo cloner.Run "telnet %IP% %PORT%", 1, False >> %VBS_FILE% 2>> %LOGFILE%

:: 【關鍵安全連線機制】
:: 腳本等待 4 秒鐘，預留給 Windows 尋找網路、與設備建立 TCP 三向交握。
:: 讓 Telnet 穩定連上並跳出終端機畫面。
echo WScript.Sleep 4000 >> %VBS_FILE% 2>> %LOGFILE%

echo Dim counter >> %VBS_FILE% 2>> %LOGFILE%
echo counter = 0 >> %VBS_FILE% 2>> %LOGFILE%

:: 輔助發送函式（每次輸入完都強制將焦點拉回 Telnet 視窗，確保指令不漏打）
echo Sub SendCmd(cmd, delay) >> %VBS_FILE% 2>> %LOGFILE%
echo     If counter ^< %totalRuns% Then >> %VBS_FILE% 2>> %LOGFILE%
echo         cloner.AppActivate "telnet %IP%" >> %VBS_FILE% 2>> %LOGFILE%
echo         cloner.SendKeys cmd ^& "{ENTER}" >> %VBS_FILE% 2>> %LOGFILE%
echo         WScript.Sleep delay >> %VBS_FILE% 2>> %LOGFILE%
echo         counter = counter + 1 >> %VBS_FILE% 2>> %LOGFILE%
echo     End If >> %VBS_FILE% 2>> %LOGFILE%
echo End Sub >> %VBS_FILE% 2>> %LOGFILE%

:: 交錯循環：每輪依序跑 ss1 → ss2 → ss3 → ss
echo Do While counter ^< %totalRuns% >> %VBS_FILE% 2>> %LOGFILE%
echo     For p1 = 0 To %num1% >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "ss 1 " ^& p1, 800 >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "at{+}eedump", 3000 >> %VBS_FILE% 2>> %LOGFILE%
echo     Next >> %VBS_FILE% 2>> %LOGFILE%

echo     For p2 = 0 To %num2% >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "ss 2 " ^& p2, 800 >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "at{+}eedump", 3000 >> %VBS_FILE% 2>> %LOGFILE%
echo     Next >> %VBS_FILE% 2>> %LOGFILE%

echo     For p3 = 0 To %num3% >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "ss 3 " ^& p3, 800 >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "at{+}eedump", 3000 >> %VBS_FILE% 2>> %LOGFILE%
echo     Next >> %VBS_FILE% 2>> %LOGFILE%

echo     For p4 = 0 To %num4% >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "ss 4 " ^& p4, 800 >> %VBS_FILE% 2>> %LOGFILE%
echo         SendCmd "at{+}eedump", 3000 >> %VBS_FILE% 2>> %LOGFILE%
echo     Next >> %VBS_FILE% 2>> %LOGFILE%
echo Loop >> %VBS_FILE% 2>> %LOGFILE%

:: 測試完畢，關閉 Telnet
echo cloner.SendKeys "^{]}" >> %VBS_FILE% 2>> %LOGFILE%
echo WScript.Sleep 500 >> %VBS_FILE% 2>> %LOGFILE%
echo cloner.SendKeys "quit{ENTER}" >> %VBS_FILE% 2>> %LOGFILE%

echo 腳本動態生成完畢。
echo [注意] 稍後跳出的黑色 Telnet 視窗會自動執行。
echo        執行期間（約 2 分鐘）請完全不要觸碰滑鼠或鍵盤，以免干擾字元輸入！
echo.
pause

:: 2. 執行 VBS 腳本
cscript //nologo %VBS_FILE% >> %LOGFILE% 2>&1

:: 3. 測試完畢後刪除暫存檔
echo 刪除暫存檔 >> %LOGFILE%
if exist %VBS_FILE% del %VBS_FILE% >> %LOGFILE% 2>&1

echo.
echo ================================================== >> %LOGFILE%
echo   測試完成 >> %LOGFILE%
echo ================================================== >> %LOGFILE%
echo   詳細紀錄看 %LOGFILE%
pause