@echo off

ResourceHacker -script %1
powershell -f %~dp0\nowtime.ps1 %2.tmp
mv %2.tmp %2