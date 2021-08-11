@echo off
@REM gen_rh_script src.dll src.res ver.res langid dst.dll output.rh

echo [FILENAMES] > %6
echo Exe=    %1 >> %6
echo SaveAs= %5.tmp >> %6
echo Log=    %5>> %6
echo [COMMANDS] >> %6
echo -addoverwrite       %2, STRINGTABLE,26,%4 >> %6
echo -addoverwrite       %3, VERSIONINFO,1,%4 >> %6