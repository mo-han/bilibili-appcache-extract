@echo off
setlocal

if '%2'=='' (
echo Usage: %~n0%~x0 input [more_input...] output
goto :eof
)
set date=%date:~,10%
set date=%date:/=%
set time=%time::=%
set time=%time:.=%
set time=%time: =0%
set ts=%date%%time%
set listfile=ffmpeg-concat-list-%ts%.txt
rem echo= >%listfile%
:roll
if '%2'=='' (
echo o: %1
set "output=%1"
goto :ffmpeg
) else (
echo i: %1
echo file '%~1' >>%listfile%
shift
goto :roll
)
:ffmpeg
ffmpeg -f concat -safe 0 -i %listfile% -c copy %output%
del %listfile%