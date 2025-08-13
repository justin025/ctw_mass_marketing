@echo off

set FOLDER_NAME=%cd%
for %%F in ("%cd%") do set FOLDER_NAME=%%~nxF
if /i "%FOLDER_NAME%"=="scripts" (
    echo You are in the scripts folder. Changing to the parent directory...
    cd ..
)

echo ========= ringcentral_mass_sms Windows Build Script =========


echo =^> Cleaning up previous builds...
del /F /Q /A dist\ringcentral_mass_sms_win_executable.exe


echo =^> Creating virtual environment...
python -m venv venvwin


echo =^> Activating virtual environment...
call venvwin\Scripts\activate.bat


echo =^> Installing dependencies via pip...
python -m pip install --upgrade pip wheel pyinstaller
pip install -r requirements.txt


echo =^> Running PyInstaller to create .exe package...
pyinstaller --onefile --noconsole --noconfirm ^
    --add-data="src/ringcentral_mass_sms/qt/qtui/*.ui;ringcentral_mass_sms/qt/qtui" ^
    --add-data="src/ringcentral_mass_sms/resources/icons/*.png;ringcentral_mass_sms/resources/icons" ^
    --paths="src/ringcentral_mass_sms" ^
    --name="ringcentral_mass_sms" ^
    src\portable.py


echo =^> Cleaning up temporary files...
del /F /Q *.spec
rmdir /s /q build __pycache__ ffbin_win venvwin


echo =^> Done! Executable available as 'dist/ringcentral_mass_sms.exe'.
