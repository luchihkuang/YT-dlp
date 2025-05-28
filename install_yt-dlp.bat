@echo off
echo 檢查 winget 是否可用...

where winget >nul 2>nul
if %errorlevel% neq 0 (
    echo 未安裝 winget，請從 Microsoft Store 安裝 "App Installer"。
    echo 下載網址: https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1
    exit /b 1
)

echo 安裝 yt-dlp 中...
winget install -e --id yt-dlp

echo 安裝完成！
yt-dlp --version
pause
