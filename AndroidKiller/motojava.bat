@echo off

color 0A
echo                ===========dex to Java===========
:start
cls

echo.请输入要处理的逆向工程名称，注意是 apk 的文件名，不是包名
set /p inputgc=

set current_dir=%~dp0

if not exist .\projects\%inputgc%\Project\build\apk\ (
echo "build文件夹未还原，请把apk文件复制到andriodkiller根目录后继续" 
pause
ren %inputgc%.apk %inputgc%.zip
call .\winrar\winrar.exe x "%inputgc%.zip" -y  "projects\%inputgc%\Project\build\apk\" && del %inputgc%.zip
) 

for /r %%i in (projects\%inputgc%\Project\build\apk\*.dex) do call .\bin\dex2jar\d2j-dex2jar.bat -f %%i && echo "反编"%%i"为jar，完成"

xcopy *.jar /y .\projects\%inputgc%\ProjectSrc\
ren *.jar *.zip
xcopy *.zip /y .\projects\%inputgc%\ProjectSrc\
del *.zip

if exist .\projects\%inputgc%\ProjectSrc\classes-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali\" && del .\projects\%inputgc%\ProjectSrc\classes-dex2jar.zip && echo "解压classes-dex2jar.jar完毕") 
if exist .\projects\%inputgc%\ProjectSrc\classes2-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes2-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes2\" && del .\projects\%inputgc%\ProjectSrc\classes2-dex2jar.zip && echo "解压classes2-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes3-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes3-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes3\" && del .\projects\%inputgc%\ProjectSrc\classes3-dex2jar.zip && echo "解压classes3-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes4-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes4-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes4\" && del .\projects\%inputgc%\ProjectSrc\classes4-dex2jar.zip && echo "解压classes4-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes5-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes5-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes5\" && del .\projects\%inputgc%\ProjectSrc\classes5-dex2jar.zip && echo "解压classes5-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes6-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes6-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes6\" && del .\projects\%inputgc%\ProjectSrc\classes6-dex2jar.zip && echo "解压classes6-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes7-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes7-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes7\" && del .\projects\%inputgc%\ProjectSrc\classes7-dex2jar.zip && echo "解压classes7-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes8-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes8-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes8\" && del .\projects\%inputgc%\ProjectSrc\classes8-dex2jar.zip && echo "解压classes8-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes9-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes9-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes9\" && del .\projects\%inputgc%\ProjectSrc\classes9-dex2jar.zip && echo "解压classes9-dex2jar.jar完毕")
if exist .\projects\%inputgc%\ProjectSrc\classes10-dex2jar.zip (call .\winrar\winrar.exe x .\projects\%inputgc%\ProjectSrc\classes10-dex2jar.zip -y  ".\projects\%inputgc%\ProjectSrc\smali_classes10\" && del .\projects\%inputgc%\ProjectSrc\classes10-dex2jar.zip && echo "解压classes10-dex2jar.jar完毕")

echo "已处理完毕" 

del /s /q .\projects\%inputgc%\project\build\

pause
