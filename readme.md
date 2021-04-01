# 一些游戏解包封包汉化工具及简单思路

## gal游戏

1. 无脑使用GARbro打开资源文件，如果可以便直接用GARbro进行解包和封包，并跳过以下所有步骤

2. 看资源后缀名：

   - rpa : renpy引擎开发，使用unrpa与unrpyc

   - xp3 :

       - 如果xp3有加密则无法用GARbro打开，但可以用XP3Viewer再游戏运行时解包及封包

       - 进行汉化时可以制作xp3补丁，如果是krkrZ可以使用KrkrExtract更方便的制作补丁

       - 如果是ks文件则可以直接编辑，或者貌似也有脚本导出器，如果是scn文件则使用ScnEditorGUI编辑，或者用FreeMoteToolkit导出源文件编辑（不建议）

3. 内存dump

4. 字体相关

   - 字体汉化
      - 改字体文件
      - 使用OllyDBG并HOOK地址

   - 字体加密

5. 其它

   - enigmaVB解包

ps:

- 逆向分析第一步：使用exeinfo（或其它类似工具）查看exe信息

## Android解包封包

1. 无脑使用AndroidKiller

2. unity逆向:

## 其它解包封包

1. 使用Extractor看能不能解出什么

2. 使用TrIDNet查看文件名（对，本人曾被一个改了后缀名的文件坑得很惨）

（未完待续）
