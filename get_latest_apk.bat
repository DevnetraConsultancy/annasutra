@echo off
echo ========================================================
echo   AnnaSutra - Download Single Universal Mobile APK
echo ========================================================
echo Target: %~dp0build_artifacts\AnnaSutra_latest.apk
mkdir "%~dp0build_artifacts" 2>nul
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
