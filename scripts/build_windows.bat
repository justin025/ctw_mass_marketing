@echo off

set FOLDER_NAME=%cd%
for %%F in ("%cd%") do set FOLDER_NAME=%%~nxF
if /i "%FOLDER_NAME%"=="scripts" (
    echo You are in the scripts folder. Changing to the parent directory...
    cd ..
)

echo ========= ctw_mass_marketing Windows Build Script =========


echo =^> Cleaning up previous builds...
del /F /Q /A dist\ctw_mass_marketing_win_executable.exe


echo =^> Creating virtual environment...
python -m venv venvwin


echo =^> Activating virtual environment...
call venvwin\Scripts\activate.bat


echo =^> Installing dependencies via pip...
python -m pip install --upgrade pip wheel pyinstaller
pip install -r requirements.txt


echo =^> Running PyInstaller to create .exe package...
pyinstaller --onefile --noconsole --noconfirm ^
    --add-data="src/ctw_mass_marketing/qt/qtui/*.ui;ctw_mass_marketing/qt/qtui" ^
    --add-data="src/ctw_mass_marketing/resources/icons/*.png;ctw_mass_marketing/resources/icons" ^
    --paths="src/ctw_mass_marketing" ^
    --name="ctw_mass_marketing" ^
    src\portable.py


echo =^> Cleaning up temporary files...
del /F /Q *.spec
rmdir /s /q build __pycache__ ffbin_win venvwin


echo =^> Done! Executable available as 'dist/ctw_mass_marketing.exe'.
