@echo off
@REM gen_rh_script src.dll src.res dst.dll output.rh

echo [FILENAMES] > %4
echo Exe=    %1 >> %4
echo SaveAs= %3.tmp >> %4
echo Log=    %5>> %4
echo [COMMANDS] >> %4
echo -addoverwrite       %2, STRINGTABLE,26,2052 >> %4