@echo off

rem
rem This compiles the PSF driver stub (psfdrv.bin) using the PSY-Q tools.
rem You MUST change the "/o 0x80xxxxxx" option under psylink to the actual
rem address where you want your stub.
rem

rem Compile.
rem Note that -G 0 is crucial here to avoid using $gp.
ccpsx -G 0 -O2 -Wall -c psfdrv.c

rem Link.
rem /o 0x80xxxxxx - origin of output. again, remember to change
rem /p            - pure binary output
rem /z            - fill BSS with zeroes
psylink /o 0x80100000 /p /z psfdrv.obj,psfdrv.bin

del psfdrv.obj
