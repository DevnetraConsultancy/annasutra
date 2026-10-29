@echo off
echo ========================================================
echo   AnnaSutra - Single Universal Mobile APK (All 7 Roles)
echo ========================================================
echo Target: %~dp0build_artifacts\AnnaSutra_latest.apk
mkdir "%~dp0build_artifacts" 2>nul

if exist "%~dp0mobile\build\app\outputs\flutter-apk\app-release.apk" (
    echo Copying freshly compiled universal APK from local Flutter release build...
    copy /Y "%~dp0mobile\build\app\outputs\flutter-apk\app-release.apk" "%~dp0build_artifacts\AnnaSutra_latest.apk" >nul
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [SUCCESS] Single Universal APK updated from local build:
        echo   %~dp0build_artifacts\AnnaSutra_latest.apk
        exit /b 0
    )
)

echo Fetching AnnaSutra_latest.apk from GitHub Release v1.0.0...
gh release download v1.0.0 --pattern "AnnaSutra_latest.apk" --dir "%~dp0build_artifacts" --clobber
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Single Universal APK updated:
    echo   %~dp0build_artifacts\AnnaSutra_latest.apk
    explorer "%~dp0build_artifacts"
) else (
    echo.
    echo [INFO] Trying direct download via curl...
    curl.exe -L "https://github.com/DevnetraConsultancy/annasutra/releases/download/v1.0.0/AnnaSutra_latest.apk" -o "%~dp0build_artifacts\AnnaSutra_latest.apk"
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [SUCCESS] Single Universal APK updated:
        echo   %~dp0build_artifacts\AnnaSutra_latest.apk
        explorer "%~dp0build_artifacts"
    )
)
