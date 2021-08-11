if not exist "%~dp0\..\tools" mkdir "%~dp0\..\tools"

cd "%~dp0\..\tools"

@REM wget https://github.com/ninja-build/ninja/releases/download/v1.10.2/ninja-win.zip
@REM unzip ninja-win.zip -d Ninja

@REM wget --content-disposition https://chrome-infra-packages.appspot.com/dl/gn/gn/windows-amd64/+/latest
@REM unzip gn-windows*.zip -d Gn

@REM wget https://www.voidtools.com/ES-1.1.0.18.zip
@REM unzip ES-*.zip -d ES

wget http://www.angusj.com/resourcehacker/resource_hacker.zip
unzip resource_hacker.zip  -d ResourceHacker

wget https://github.com/gerardog/gsudo/releases/download/v0.7.3/gsudo.v0.7.3.zip
unzip gsudo.v0.7.3.zip -d gsudo