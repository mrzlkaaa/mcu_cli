@echo off

rem Check PATHes to EXE and MCUDBxx below!
set pathexe=C:\MCUKOSMOS\EXE\
set  pathdb=C:\MDBKOSMOSRF\

rem batch file to run mcu state calculations       
rem the 1-st parameter is f (fimtoen) or m (mofittg)      
rem the 2-nd parameter is name of the variant     
rem the 3-d  parameter is a key that may be:      
rem a  - do all steps
rem i  - do input only             
rem c  - do calculation only             
rem f  - do final processing only             
rem b  - do burnup step
rem d  - delete files created by previous run 


if "%3" == "d" goto delall
if "%3" == "D" goto delall

if "%1" == "f" goto okth
if "%1" == "F" goto okth
if "%1" == "m" goto okth
if "%1" == "M" goto okth
@echo wrong version of thermal submodule (f-fimtoen, m-mofittg)
pause
goto stop
:okth

if "%2" == "" goto err1
if not exist %2 goto err2

echo %2 >mcu5.ini
echo %pathdb%>>mcu5.ini
if not "%3"=="" echo %3 >>mcu5.ini

:start
%pathexe%mcu_%1.exe
goto stop

:err1
echo error: no parameters in the command line.
goto stop     
    
:err2
echo error: input data file %2 cannot be found
goto stop     

:delall
cls
echo Deleting %2.* and other files of previouse mcu run.
echo Press Ctrl+C to abort.
pause
if exist %2 copy %2 mcu5.sys >nul
if exist %2.* del %2.*
if exist end_time del end_time
if exist step_end del step_end
if exist no_sigma del no_sigma
if exist mcuname del mcuname
if exist energy.fis del energy.fis
if exist *.bur del *.bur
if exist mcu5.sys copy mcu5.sys %2 >nul
if exist mcu5.sys del mcu5.sys
if exist mcu5.ini del mcu5.ini
echo Done.
goto stop

:stop

