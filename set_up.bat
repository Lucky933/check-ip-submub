@echo off
setlocal enabledelayedexpansion

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Dang yeu cau quyen Administrator...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~dpnx0' -Verb RunAs"
    exit /b
)
echo ===== Bat dau cai dat Python va cac thu vien can thiet =====
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python chua duoc cai dat. Dang tai xuong Python 3.10.11...
    
    if not exist "temp\" mkdir "temp"
    
    echo Dang tai xuong Python 3.10.11 64-bit...
    curl -L "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" -o "temp\python_installer.exe"
    if not exist "temp\python_installer.exe" (
        echo Khong the tai xuong Python installer.
        pause
        exit /b 1
    )
    echo Dang cai dat Python 3.10.11...
    temp\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    echo Dang cho cai dat hoan tat...
    timeout /t 30 /nobreak
    call refreshenv.cmd >nul 2>&1
    if %errorlevel% neq 0 (
        set PATH=%PATH%;C:\Program Files\Python310;C:\Program Files\Python310\Scripts
    )
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python chua duoc cai dat thanh cong. 
        echo Ban co the can khoi dong lai may tinh.
        pause
        exit /b 1
    ) else (
        echo Python da duoc cai dat thanh cong!
    )
) else (
    echo Python da duoc cai dat.
)
echo.
echo Dang cai dat cac thu vien can thiet...
python -m pip install --upgrade pip
python -m pip install geoip2

echo.
echo ===== DONE =====
echo.
if exist "temp\" rmdir /s /q "temp"
pause