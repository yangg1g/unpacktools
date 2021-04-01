@echo off
TITLE AndroidKiller_v1.3.1自动ADB连接蓝叠模拟器工具 by 吾爱论坛 昨夜星辰2012

color 3f 

:MENU
CLS
@ ECHO.
@ ECHO =================================================
@ ECHO 出处:https://www.52pojie.cn/
@ ECHO.
@ ECHO =================================================
@ ECHO.
@ ECHO 以下将自动开始通过ADB命令连接蓝叠模拟器
@ ECHO.
@ ECHO 请确认是否已经将AK目录下bin\adb文件夹中的3个文件复制到蓝叠模拟器目录
@ ECHO.
@ ECHO 请确认蓝叠模拟器的安装路径是C:\Program Files\BluestacksCN
@ ECHO.
@ ECHO 请确认C:\Program Files\BluestacksCN\Engine\ProgramFiles目录下有HD-ADB.exe文件
@ ECHO.
@ ECHO 信息完全一致，请按Y → 回车键继续
@ ECHO.
@ ECHO 信息不一致，请按N → 回车键关闭窗口，修改本批处理文件后重新运行
@ ECHO.
@ ECHO =================================================

:CHO
set choice=
set /p choice= 选择你要进行的操作:
IF NOT "%Choice%"=="" SET Choice=%Choice:~0,1%
if /i "%choice%"=="Y" goto 1
if /i "%choice%"=="N" goto 2
echo 选择无效，请重新输入
echo.
goto MENU

:1
CLS
COLOR E0
ECHO. =================================================
echo.
echo   正在操作中，操作完成后按任意键关闭窗口
echo.
ECHO. =================================================
@ taskkill /im adb.exe /f 

>nul 2>nul 上方的命令作用是结束adb进程，不用修改

@ taskkill /im hd-adb.exe /f

>nul 2>nul 上方的命令作用是结束hd-adb进程，这个进程是蓝叠模拟器特有的，其他模拟器应该没有，不用修改

@ cd /d C:\Program Files\BluestacksCN\Engine\ProgramFiles 

>nul 2>nul 上方命令的作用是改变当前目录hd-adb.exe所在的C:\Program Files\BluestacksCN\Engine\ProgramFiles目录（蓝叠的默认目录是这个）如果你的目录不一样，请按实际路径修改命令的后半部分

@ hd-adb connect 127.0.0.1：5555 

>nul 2>nul 上方命令的作用是启动hd-adb.exe进程，并通过5555端口进行连接，蓝叠是5555默认adb端口，其他模拟器请自行修改对应的端口号

CLS
COLOR 3f
CLS
@echo 已处理完毕 
ECHO. =================================================
echo.
echo   操作完成，按任意键关闭窗口
echo.
ECHO. =================================================

pause

:2
CLS
COLOR E0
echo ***************************************************************************
echo *                                                                         *
echo *                                                                         *
echo *                        即将关闭窗口                                     *
echo *                                                                         *
echo *                                                                         *
echo *                                                                         *
echo ***************************************************************************

pause 
