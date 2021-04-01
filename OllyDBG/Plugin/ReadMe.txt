

		OllyDBG v1.10 plugin  - StrongOD v0.3.9
			by 海风月影[CUG]
====================================================================
[2010.12.29 v0.3.9.706]
1，增强反反调试
2，修复部分BUG
3，优化窗口刷新


[2010.10.10 v0.3.7.666]
1，增强反反调试
2，修复部分BUG
3，执行脚本时，OD可以最小化


[2010.08.17 v0.3.6.650]
1，修复一个驱动可能的蓝屏BUG
2，防止OD被postmessage关闭
3，修复分析PE的一个BUG
4，驱动转移到数据段


[2010.06.24 v0.3.5.639]
1，Add AutoUpdate


[2010.06.13 v0.3.4.633]
1，优化解决OD调试卡死的BUG
2，驱动释放到插件目录
3，增加PatchOD功能，od所有窗口类名随机化，避免被检测
4，cmdbar的窗口名采用Draw的方式画出来，避免被检测
5，修复导入表处理的一处BUG
6，解决cmdbar与Ollyskin不兼容的问题


[2010.04.28 v0.3.3.625]
1，解决OD在调试游戏时非常容易卡死的BUG


[2010.03.26 v0.3.2.616]
1，优化了Mem窗口数据的保存，mem2 - mem5的数据类型会被保存下来
2，修复获取codesize的一个BUG
3，界面微调，优化toolbar的字体


[2010.03.05 v0.3.1.610]
1，修复了一个anti-anti的BUG，以及其他的一些小BUG
2，Splash可以自定义，在ollydbg.ini中加入
[Plugin StrongOD]
logo = c:\ollydbg\Splash1.bmp
默认是加载ollydbg.exe目录下的Splash.bmp

3，cmdbar可以用tab键快速选命令

比如，a开头的命令有 asm at ac attach等
输入a，然后按tab，就可以切换a开头的所有命令：at a asm ac attach
输入at，然后按tab，就可以切换at开头的所有命令：at attach


4，alt+Q快捷键是在目标进程内申请内存，在配置里面可以设置默认大小
[Plugin StrongOD]
AllocSize = 10
读取的值是16进制的，申请内存的大小是 AllocSize * 0x1000，默认情况下AllocSize = 1

5，增加新命令：ALLOC [AllocSize]，在目标进程内申请内存，内存大小是 AllocSize * 0x1000

如果没有指定 AllocSize，则读取配置文件中的值
如果配置文件中没指定，默认为1


[2010.01.08 v0.2.9.561]
1，命令行增加Attach <pid>和Detach两个功能，pid是10进制的
2，去除alt + 1 ~ 9都是nop的功能
3，驱动隐藏窗口算法优化
4，增加兼容性，去掉关file句柄的功能
5，修复几个小BUG


[2010.01.08 v0.2.9.561]
1，命令行增加Attach <pid>和Detach两个功能，pid是10进制的
2，去除alt + 1 ~ 9都是nop的功能
3，驱动隐藏窗口算法优化
4，增加兼容性，去掉关file句柄的功能
5，修复几个小BUG

[2009.11.26 v0.2.8.478]
1，关掉OD不需要的句柄(有些dll句柄被od锁定了)
2，优化cpu dump窗口功能
3，mem窗口数据保存（保存M2-M5）
4，增加dump窗口快捷键（CTRL+B搜索出来的dump窗口，可以用快捷键，快速切换到cpu dump窗口）
5，优化启动速度

[2009.10.28 v0.2.7.433]
1，win7，2003下修复anti_anti attach功能
2，win7下特权指令过滤
3，驱动通信加密
4，增加快捷键ctrl+d，将焦点设置到cmdbar上
5，修复几个小BUG
6，cmdbar界面小小改动

[2009.09.01 v0.2.6.413]
1，添加加载微软符号库的选项
2，Cmdbar增加命令MSG，显示消息号

[2009.08.26 v0.2.6.410]
1，集成Command Bar功能(快捷键改成ALT+F1)，可以抛弃cmdbar插件了
2，Cmdbar和TBAR插件兼容

[2009.08.24 v0.2.6.405]
1，全面支持win7(7600以下版本不支持)
2，增强解析PE的稳定性
3，修复tmd壳某些时候attach上去无法下断点的漏洞

[2009.06.16 v0.2.5.388]
1，增加ring0稳定性
2，尝试杀掉NP线程

[2009.06.13 v0.2.5.384]
1，修复驱动几个bug，去掉字符串
2，稳定性增加，不再需要key

[2009.04.24 v0.2.4.364]
1，驱动有很大改动，加了一些功能，与以前的StrongOD不兼容，更新后需要重启机器
2，启动时检查ollydbg中的可疑线程
3，继续修改attach功能
4，修复加壳后无法使用远程注入的功能


[2009.04.03 v0.2.4.350]
1，修复驱动在某些2000下蓝屏的BUG
2，修复驱动的几个BUG
3，加key验证，需要StrongOD.key才能运行

[2009.03.30 v0.2.4.347]
1，修复vista下attach异常的问题
2，增强attach的稳定性，Attach后需要F9，然后resume all thread
3，advenummod支持动态卷，网络映射盘
4，vista sp1下无法打开文件的bug
5，vista下父进程修改

[2009.03.17 v0.2.4.341]
1，退出OD去掉ZwOpenThread的hook
2，修复OD处理codebase会崩溃的BUG
3，驱动不会影响非OD调试程序的情况

[2009.03.09 v0.2.3.328]
1，增强进程保护(保护线程)，省得老毛子麻烦
2，修复一个导入表分析的错误
3，修复处理重定位表的BUG
4，修复attach notepad.exe的BUG
5，修复处理导出表的bug
6，修复处理tls的BUG

[2009.02.14 v0.2.3.314]
1，修复了2003 sp1下蓝屏bug(感谢cxh852456)
2，增强快捷键兼容性，支持简单修改版的OD

[2009.02.10 v0.2.3.305]
1，修复几个小BUG
2，增强attach功能
3，修复某个BUG

[2009.02.04 v0.2.3.301]
1，底部快捷栏自动记录是否隐藏
2，底部状态栏显示Memory窗口状态
3，修复驱动不加载的bug

[2009.02.01 v0.2.3.299]
1，增加多个内存窗口的快速切换，快捷键 alt+1 ~ alt+5
2，增加切换堆栈窗口关联到ebp寄存器或者不关联任何寄存器，快捷键 alt+1 ~ alt+3
3，增加一个底部的快捷栏，上面有快速切换的按钮，Option里面可以取消创建这个快捷栏，
	如果创建后可以用Alt+R来显示，隐藏快捷栏
4，底部的快捷栏是否创建，不影响上面快速切换的功能（没有按钮可以用快捷键来切换）

[2009.01.14 v0.2.2.292]
1，修复一些解析PE的小bug
2，修复内存断点判断的一个小bug

[2009.01.14 v0.2.2.283]
1，修复一些小bug
2，修复驱动一个bug

[2009.01.11 v0.2.2.275]
1，增加选项删除入口点断点
2，增加选项中断在Tls入口（如果有的话），必须选上Kill Pe Bug
3，增加选项中断在进ring3的第一行代码（是否实现，待定）
4，配置文件中增加OrdFirst，决定mfc42中的导出函数是序号优先还是名字优先
5，修复处理重定位表的bug
6，Attach窗口的鼠标滚轮改成WM_VSCROLL消息

[2009.01.08 v0.2.1.273]
1，修正处理导出表和导入表的bug
2，修正处理重定位表的bug
3，修复Skip Some Expection选上的时候对内存段下F2断点无法正常断下的bug
4，修复Skip Some Expection选上的时候内存断点无法断下的BUG
5，修复IAT中序号找不到函数名的BUG

[2009.01.06 v0.2.1.262]
1，增加Attach窗口的鼠标滚轮支持
2，重写od处理模块的代码

[2008.12.30 v0.2.1.252]
1，修复驱动BUG

[2008.12.25 v0.2.1.235]
1，修复一个利用PAGE_GUARD的anti
2，修复Skip Some Expection选上的时候无法对内存段下F2断点
3，由于PAGE_GUARD的特殊性，无法完美处理od用PAGE_GUARD下断点的BUG，建议尽量不要对内存段下F2断点
4，加强进程保护功能，防止ring3下复制句柄打开od进程
5，修复驱动多处小bug
6，更新版本号

[2008.11.06 v0.20]
1，超长异常处理链导致OD打开太慢的BUG

[2008.11.03 v0.19]
1，增加一个快捷键，cpudump 窗口 alt+左键双击
2，修复隐藏OD窗口后输入法有可能无法使用的BUG
3，修复了一个潜在的蓝屏BUG


[2008.09.15 v0.18]
1，修复了Ctrl+G计算rva,offset时的一个小BUG
2，当程序不是运行的状态时，Detach前会先运行程序
3，修复原版OD的数据区复制BUG
4，修复od运行后CPU占用率很高的BUG
5，可以设置是否跳过一些异常处理

[2008.09.02 v0.17]
1，跳过不是OD设的Int 3中断，跳过STATUS_GUARD_PAGE，STATUS_INVALID_LOCK_SEQUENCE异常
2，正确处理int 2d指令

[2008.08.31 v0.16]
1，加入驱动，保护进程，隐藏窗口，过绝大部分反调试
2，驱动支持自定义设备名（ollydbg.ini中的DeviceName，设备名不超过8个字符）
		ollydbg.ini中的[StrongOD]中，可以自己设定
		HideWindow=1 					隐藏窗口
		HideProcess=1					隐藏进程
		ProtectProcess=1			保护进程
		DriverKey=-82693034		和驱动通信的key
		DriverName=fengyue0		驱动设备名(不超过8个字符)

3，将OD创建进程的父进程改成explorer.exe (抄自shoooo的代码)

[2008.08.10 v0.15]
1，增强查找模块功能（能正确查找处理过peb的模块，比如ring3的隐藏模块）
2，增强OD对文件Pe头的分析（如Upack壳等）
3，anti anti attach （一种极端的attach方式）
4，脱离目标程序不再调试（DebugActiveProcessStop）功能，xp系统以上
5，注入dll到被调试的进程
	a) Remote Thread（使用CreateRemoteThread注入）
	b) Current Thread（shellcode，不增加线程方式注入，当前线程必须暂停）


[2008.07.04 v0.14]
1，过VMP 1.64邪恶anti
下载地址：http://www.unpack.cn/viewthread.php?tid=26870

[2008.01.20 v0.13]
1，Advanced Ctrl + G 功能可以输入API名(已经和OD自带的功能一摸一样了)
2，修复了当没有断点的时候会有删除所有断点的选项的BUG
3，修复了删除所有断点，有可能删不完的BUG
4，当线程小于或等于1的时候，不会有Resume all thread 和 Suspend all thread选项
5，并不兼容看雪9.21版本(因为这个版本修改了ACPUASM等类名，如果自己修改的版本请不要修改ACPU这样的类名)
6，和加壳版的OD有一定的兼容性（载入时将导入表写回PE头和相应的位置，但还是不支持TheODBG）


[2008.01.15 v0.12]
1，增加了Advanced Ctrl + G 功能
2，将浮点bug作为选项(patch代码的，需要重启才能保存选项)
3，将原本patch的代码都取消，全部改成hook形式，增加兼容性(后续的功能将都用patch的形式做)


[2007.11.15 v0.11]
去除了2个BUG：
1，启动程序时，如果目录有空格会有个出错信息
2，CPU DUMP 窗口，如果选中一个内存块的第一个字节，Infoline会显示异常

增加：
如果断点窗口没有任何断点，则不显示菜单


[2007.11.14 v0.10]
增加创建进程模式

本插件提供了3种方式来启动进程:

1,Normal
	和原来的启动方式相同，清掉了STARTINFO里面不干净的数据

2,CreateAsUser
	用一个User权限的用户来启动进程，使进程运行在User权限下，无法对Admin建立的进程进行操作
	运行这个需要在本地安全策略－用户权利指派里面将你的用户加入2个权限：
		1，替换进程级记号(SeAssignPrimaryTokenPrivilege)
		2，以操作系统方式操作(SeTcbPrivilege)
	如果是home版的windows，无法设置，那么可以试试使用SuperMode，重启OD来提升权限，强烈不建议使用这个选项

3,CreateAsRestrict
	第二个选项用User权限的用户来启动进程限制的地方比较多，所以，增加第三个功能，以一个限制级的Admin用户来启动程序
	启动的程序是以Admin的用户，不过权限只剩下默认User用户有的权限，一些危险权限全部删除（包括SeDebugPrivilege，SeLoadDriverPrivilege等），这样运行的程序不会对OD造成很大的伤害。建议用这个方式启动程序。


注意：
1，新增加的这2个启动方式，不一定能运行所有的程序（比如OllyDbg）！不过在调试木马的时候会有不错的效果。
2，和 Olly Advanced 插件冲突，加载了Olly Advanced 插件，此功能失效！



隐藏调试器功能
HidePEB，去掉PEB中的调试标记，并且从根本上解决了HeapMagic的问题(参考的Phant0m.dll)

此功能的选项选不选都自动隐藏


快捷键功能


1. 增加CPU ASM，CPU DUMP，CPU STACK窗口中增加Enter相关的一系列快捷键

CPU ASM窗口中
例如 
1000481A  |.  A3 F48E0010   mov     dword ptr ds:[10008EF4], eax


选中这行时，按Enter，       表示在 CPU DUMP窗口显示10008EF4位置
	    按Shift+Enter， 表示在 CPU ASM 窗口显示10008EF4位置
	    按Ctrl+Enter，  表示在CPU DUMP窗口显示这行的地址1000481A位置

如果有2个立即数，比如

1000481A mov dword ptr ds:[10001000],40304C 

这样的语句，如果要切换另一个立即数，就加上Alt，进行切换

选中这行时，按Enter，           表示在 CPU DUMP窗口显示40304C位置
	    按Shift+Enter，     表示在 CPU ASM 窗口显示40304C位置
	    按Ctrl+Enter，      表示在 CPU DUMP窗口显示这行的地址1000481A位置
	    按Alt+Enter，       表示在 CPU DUMP窗口显示10001000位置
	    按Alt+Shift+Enter， 表示在 CPU ASM 窗口显示10001000位置

CPU DUMP窗口中

按Enter，表示在CPU ASM窗口显示选中的第一个字节开始的数据内容
按Shift+Enter，表示在CPU DUMP窗口显示选中的第一个字节开始的数据内容
按Ctrl+Enter，表示在CPU ASM窗口显示选中的第一个字节的地址

CPU STACK窗口中

按Enter，表示在CPU ASM窗口显示选中行的数据
按Shift+Enter，表示在CPU DUMP窗口显示选中行的数据
按Ctrl+Enter，表示在CPU ASM窗口显示选中行的地址
按Alt+Enter，表示在CPU DUMP窗口显示选中行的地址


2. 增加CPU ASM , CPU DUMP , CPU STACK窗口快捷键ESC和`(注:ESC下面的),此按键功能同在CPU窗口按-(减号)+(加号)功能.（方便笔记本，因为笔记本没有小键盘）
3. 增加CPU REG窗口快捷键ESC和`(注:ESC下面的)实现View FPU,View MMX,View 3D Now!,View Debug的快速翻页.
4. 增加CPU STACK窗口快捷键ESC和`(注:ESC下面的),ESC表示在CPU STACK窗口显示ESP值，`表示显示EBP的值
5. 增加CPU REG窗口快捷键CTRL+数字键1至8(分别对应EAX,ECX,EDX,EBX,ESP,EBP,ESI,EDI)将其内容显示在CPUASM窗口中
   增加CPU REG窗口快捷键SHIFT+数字键1至8(分别对应EAX,ECX,EDX,EBX,ESP,EBP,ESI,EDI)将其内容显示在CPUDUMP窗口中
		

6. 增加CPU ASM,CPU DUMP窗口快捷键Shift+C,Shift+V,Shift+X,Ctrl+X.分别对应二进制复制,二进制粘贴,无空格二进制复制(方便写OD脚本的兄弟)，复制选中的第一个字节的地址
   注:Shift+V 只需要选中起始地址即可.
   Shift+C与Shift+X的区别如下:
   55 8B EC 8B 45 0C 48 74 42 48 74 37 83 E8 0D 74 
   558BEC8B450C48744248743783E80D74

   Ctrl+X功能是复制选中的第一个字节的地址，如选中的第一行是

1000481A mov dword ptr ds:[10001000],40304C 

按Ctrl+X，则地址01000481A 复制到剪贴板

7. 增加在CPU ASM 和CPU DUMP窗口增加快捷键Insert ,Delete

	Insert 将选中的区域以0x90填充
	Delete 将选中的区域以0x00填充

先选中一块区域，然后按键，填充完后可以用OD的恢复功能恢复(Alt + Backspace)



8. 增加状态栏显示CPU DUMP窗口中选中区域的起始地址,结束地址,选中区域大小,及当前值.

注:如CPU DUMP窗口数据为00401000  00 10 40 00 69 6E 67 20 鼠标选中地址00401000后面的00时,状态栏窗口显示Value为401000,按Ctrl+双击鼠标左键复制Value到剪切板.


9. 增加断点窗口(ALT+B呼出)Delete All BreakPoints功能.实现删除全部断点.
10. 增加线程窗口Suspend All Threads,Resume All Threads功能.实现挂起和恢复全部线程.


特别感谢：fly,sucsor,lifeengines,shoooo,foxabu,hellsp@wn,okdodo,kanxue,a__p,微笑一刀,goldsun




