# =====================================================================================================
# Extremely basic ssf combiner script (ver 0.14 2008-10-12) by kingshriek
# Combines driver, area map data, tone data, sequence data, and DSP program into a ssf file.
# Requires bin2psf & psfpoint (http://www.neillcorlett.com/psf/utilities.html)
# Update history located near end of file
# =====================================================================================================

# =====================================================================================================
# There are 6 things that a ripper needs to concern him(/her)self with when ripping SSFs from the game data itself.
#    (1) Sound driver - 68000 executable, usually called SDDRVS.TSK (or something with "SDDRVS" in it). Sometimes the 
#        driver will be embedded in a larger file. The driver's reset handler almost always starts with a 
#        MOVE #0x2700,SR instruction which disables interrupts (and if it doesn't, it will be very close to beginning 
#        of the reset code). Search for the hex data "46 FC 27 00". After finding it, if you see some version information 
#        (ASCII text) not too far away, you have almost certainly found the sound driver. The reset handler will most 
#        likely start at 0x1000 in 68000 RAM, so go 4096 bytes backwards from "46 FC 27 00" (68000 RAM location 0x0000) 
#        and you'll most likely find the hex data "00 00 A0 00 00 00 10 00" - the sound driver begins here. From this 
#        location, extract 28,672 bytes to successfully isolate the sound driver.
#    (2) Sound area map - This tells the driver how to interpret different regions of sound memory; mapped to 
#        0x500-0x5FF in the 68000's address space. Consists of eight byte blocks, containing the type of data 
#        (sequence, tone, DSP program, or DSP RAM), bank number, offset, transfer complete status, and size. The 
#        transfer complete bits need to be set by the ripper for sound driver to function correctly. More specifically,
#        the 0x500-0x5FF region is actually where the current in-use area map as located, although the area map data
#        itself is actually transferred to 0xA000-0xAFFF first (usually multiple area maps). When the game engine issues
#        a MAP_CHANGE command, the selected area map from 0xA000-0xAFFF is transferred to the current area map location
#        (0x500). For SSF rips, it is recommended that the current area map be placed directly into the 0x500 rather than
#        using 0xA000-0xAFFF and issuing a MAP_CHANGE command. The reason for this is that in addition to a MAP_CHANGE
#        command, the game program must also tell the sound driver that the correct sound data has been transferred into
#        memory via setting the transfer complete bits in the current area map region (0x500-0x5FF) and this can't be
#        accounted for in a SSF (68000 only) without hacking the sound driver.
#    (3) Sequence data - Sound area map determines where this is mapped. Multiple tracks may exist in the data (number of 
#        tracks is given by the 2nd byte in the sequence data). If they are stored on the game CD as single files, they'll 
#        usually either have the extension "SEQ" or have "SEQ" in the name somewhere. Some games pack a lot of sequence data 
#        into larger archives. If they exist in these archives in a uncompressed form, use the seqext.py script to extract them.
#    (4) Tone data - Sound area map determines where this is mapped. Sequence data may reference tone data from 
#        multiple tone files - be careful here (you can use ssfinfo.py to check). If they are stored on the game CD 
#        as single files, they'll usually either have the extension "BIN"/"TON" or have "BIN"/"TON" in the name somewhere. 
#        Some games pack a lot of tone data into larger archives. If they exist in these archives in a uncompressed form, use 
#        the tonext.py script to extract them.
#    (5) DSP programs (if any) - Sound area map determines where this is mapped. If they are stored on the game CD as single
#         files, they'll usually either have the extension "EXB" or have "EXB" in the name somewhere. DSP program data typically 
#         has the name of the DSP program embbedded at the beginning (usually <something>.EXB or <something>.EX). DSP programs 
#         are usually (maybe always) 1344 bytes in size. The SCSP DSP does not execute a DSP program from sound RAM directly.
#         A EFFECT_CHANGE commands first needs to be issued by the game program for the DSP program to be uploaded to the DSP.
#    (6) Sound commands sent to the driver from the host - 0x700-0x77F in the 68000 address space acts as a buffer for 
#        8 sound commands (each being 16 bytes in length - first byte determines the command, second byte is zero, the 
#        rest are parameters). The ripper will most likely need to manually produce these. A common command set to initialize
#        sequence playback consists of four commands: MIXER_CHANGE, EFFECT_CHANGE, SEQUENCE_START, and
#        SEQUENCE_VOLUME, which this script is set up to do by default. 
#
# For (1)-(5), the user specifies file names in the parameter section below. (6) is handled by the non-file name 
# parameters. There are cases where not all the data needs to be explicitly specified by the user. See the notes
# below for more information.
# -----------------------------------------------------------------------------------------------------
# The script supports ssflib/minissf (in simple situations where only the bank or track numbers are changed) as well 
# as plain ssfs. To accomodate this, another parameter, an output file name, is required from the user. To use 
# ssflib/minissf, just have the output file name end in '.ssflib'. The script will then generate an ssflib file and a 
# minissf for each track in the user-selected bank. minissf files are outputted in the format 
# <filename>_bank_track.minissf. minissf creation requires the PSFPoint utility, available at PSF Central
# (http://www.neillcorlett.com/psf/utilities.html).
# -----------------------------------------------------------------------------------------------------
# Also, the bulk of the script is defined as a function, which is called at the very bottom. Feel free to customize this
# bottom section as you wish. Once good use for it is that you can write some code to loop over a bunch of files and 
# perform the ssf creation in batch mode.
# -----------------------------------------------------------------------------------------------------
# NOTE: If using a DSP program, make sure the area map allocates enough RAM for the ring buffer and any coefficient
#      tables (if present). You can check DSP RAM requirements with ssfinfo.py (as of v0.02). Failure to specify enough
#      DSP RAM will result in the driver rejecting the DSP program. Also, make sure a suitable mixer is selected. If
#      the selected mixer contains zero values for the effect send levels, effects will not be applied. ssfinfo.py can
#      be used to check mixer settings.
#
# NOTE: Area map data doesn't necessarily need to come from the game's data/files. In cases the sound 
#      data (driver, sequence data, tone data, DSP program) can be isolated, it is usually enough to use a 
#      general-purpose area map. I have provided six with the script - all of which use any of banks 0-7.
#      Details on the area maps are as follows:
#          (without DSP)
#          GEN_SEQ10000.MAP        0x65000 bytes TONE, 0x10000 bytes SEQUENCE
#          GEN_SEQ20000.MAP        0x55000 bytes TONE, 0x20000 bytes SEQUENCE
#          (with DSP)
#          GEN_DSP4040.MAP         0x60FC0 bytes TONE, 0xF000 bytes SEQUENCE, 0x1000 bytes DSP_PROGRAM, 0x4040 bytes DSP_RAM
#          GEN_DSP8040.MAP         0x5CFC0 bytes TONE, 0xF000 bytes SEQUENCE, 0x1000 bytes DSP_PROGRAM, 0x8040 bytes DSP_RAM
#          GEN_DSP10040.MAP        0x54FC0 bytes TONE, 0xF000 bytes SEQUENCE, 0x1000 bytes DSP_PROGRAM, 0x10040 bytes DSP_RAM
#          GEN_DSP20040.MAP        0x44FC0 bytes TONE, 0xF000 bytes SEQUENCE, 0x1000 bytes DSP_PROGRAM, 0x20040 bytes DSP_RAM
#      If you are getting a warning about bank overflow or DSP RAM requirements after using one of these, try using a
#      different map with either more tone data DSP RAM space. You may wish to modify one of these provided area maps if all 
#      of them are producing overflow warnings - see the area map info below if you wish to do this. One thing to keep in mind 
#      is that these general area maps as provided will only support sequence data that references a single tone bank - for 
#      those that don't, you will either have to use one extracted from the game data or create a custom one.
#
# NOTE: Although the script is primarily set up for games that store bank/sequence/DSP data in separate
#       files, it can handle combined data files in certain situations. Some games store combine sound data
#       into larger files that are mapped directly into sound memory. To handle these, determine the bank
#       and type (sequence data, tone data, DSP program)  of the first instance of sound data in the file
#       according to the area map and set the corresponding filename parameter to the name of the file
#       while setting the other data file name parameters to an emptry string. The script will produce a 
#       warning about data overflowing the area map, but the data will still be copied anyway so just
#       ignore it.
#
# NOTE: The script is really only set up to handle a single bank of tone data (matching the sequence bank).
#       Some games contain sequences that reference multiple tone banks. To handle these, the script
#       needs to be run multiple times (each time with a different tone data file and bank #). Each time
#       script is run, a file named 68000ram.bin will be dumped out. This is a 512K file that corresponds
#       to sound memory. For additional runs, just set the driver file name to this file ('68000ram.bin')
#       as well as setting the corresponding bank numbers and tone data files, leaving the other file name
#       parameters blank. Finally, the last pass of the script needs to have the bank number set to the 
#       desired sequence bank since the script always writes this value into the SEQUENCE_START command.  
# =====================================================================================================

# =====================================================================================================
# Area map format
# -----------------------------------------------------------------------------------------------------
# The currently used area map resides at 0x500-0x5FF in the 68000's address space. The area map consists of
# units of 8-byte blocks (so 32 at most). The format of one of these blocks is as follows:
#
#     fb aa aa aa t0 ss ss ss
#
#     f - Data format (4-bits - 0: TONE, 1: SEQUENCE, 2: DSP_PROGRAM, 3: DSP_RAM)
#     b - Bank number (4-bits - any value between 0-15)
#     a - Start address (24-bits, big-endian, if DSP_RAM, must be a multiple of 0x2000)
#     t - Transfer bit (bit 7 - must be set to 1 for the driver to read the data)
#     s - Data size (24-bits, big-endian)
#
# If DSP_PROGRAM banks are included, there must be a DSP_RAM bank present. The DSP_RAM bank must be large
# enough to meet the DSP_PROGRAM requirements. The DSP RAM size is specified by byte 0x20 in the DSP program 
# header (0: 0x4040 bytes, 1: 0x8040 bytes, 2: 0x10040 bytes, 3: 0x20040 bytes). Also, the start address
# for a DSP RAM bank must be a multiple of 0x2000 bytes.
# =====================================================================================================

# =====================================================================================================
# PARAMETERS
bank      = 0x00    # sequence bank number
track     = 0x00    # sequence track number
volume    = 0x7F    # volume (reduce if clipping)
mixerbank = bank    # mixer bank number (usually same as sequence bank number)
mixern    = 0x00    # mixer number (usually 0)
effect    = 0x00    # effect number (usually 0)
use_dsp   = 1       # 1: use DSP, 0: do not use DSP
# -----------------------------------------------------------------------------------------------------
# filenames - use an empty string if file isn't needed
ndrv = ''    # sound driver
nmap = ''    # sound area map
nbin = ''    # tone data
nseq = ''    # sequence data
nexb = ''    # DSP program 
# -----------------------------------------------------------------------------------------------------
nout = 'ssfdata.ssf'    # output file name (if .ssflib, create ssflib and minissfs for each track in the bank)
# =====================================================================================================

# =====================================================================================================
from struct import *    # pack, unpack
from array import *    # array
import os    # system, path
# =====================================================================================================

# =====================================================================================================
# Converts list of bytes into a sound command list (zero-padded out to 16 bytes)
def sndcmd(x):
	if len(x) > 0x10:
		x = x[:0x10]
	return array('B',x + [0x00]*(0x10-len(x)))
# =====================================================================================================

# =====================================================================================================
# Get base file name with and without extension
def fnoext(fname):
	fnameb = os.path.basename(fname)
	idot  = -fname[::-1].find('.')-1
	if idot:
		fnamex = fnameb[:idot]
	else:
		fnamex = fnameb
	return (fnameb,fnamex)
# =====================================================================================================

# =====================================================================================================
# Creates ssf file from user-specified parameters.
# Inputs are defined in paramter section above.
def ssfmake(nout,ndrv,nmap,nbin,nseq,nexb,bank,track,volume,mixerbank,mixern,effect,use_dsp):
	# Initialization
	szdrv = 0
	szmap = 0
	szbin = 0
	szseq = 0
	szexb = 0
	datadrv = array('B',[])
	datamap = array('B',[])
	databin = array('B',[])
	dataseq = array('B',[])
	dataexb = array('B',[])
	aseq = None
	ntracks = 0
# -----------------------------------------------------------------------------------------------------
	if ndrv != '':
		fdrv = open(ndrv,'rb')    # sound driver
		szdrv = os.path.getsize(ndrv)
		datadrv = array('B',fdrv.read(szdrv))
		fdrv.close()
	if nmap != '':
		fmap = open(nmap,'rb')    # sound area map
		szmap = os.path.getsize(nmap)
		datamap = array('B',fmap.read(szmap))
		fmap.close()
	if nbin != '':
		fbin = open(nbin,'rb')    # tone data
		szbin = os.path.getsize(nbin)
		databin = array('B',fbin.read(szbin))
		fbin.close()
	if nseq != '':
		fseq = open(nseq,'rb')    # sequence data
		szseq = os.path.getsize(nseq)
		dataseq = array('B',fseq.read(szseq))
		fseq.close()
	if nexb != '':
		fexb = open(nexb,'rb')    # DSP program
		szexb = os.path.getsize(nexb)
		dataexb = array('B',fexb.read(szexb))
		fexb.close()
# -----------------------------------------------------------------------------------------------------
	ssfbin = array('B','\x00'*0x80000)
# -----------------------------------------------------------------------------------------------------
	# Set driver
	ssfbin[:szdrv] = datadrv
# -----------------------------------------------------------------------------------------------------
	# Set area map
	ssfbin[0x500:0x500+szmap] = datamap
	offset = 0x504
	# Set transfer complete bits
	while offset < 0x600:
		ssfbin[offset] = 0x80
		offset += 0x8
# -----------------------------------------------------------------------------------------------------
	# Set sound commands
	ssoffset = 0x770    # SEQUENCE_START offset (for minissf)
	ssfbin[0x700:0x710] = sndcmd([0x87,0x00,mixerbank,mixern])        # MIXER_CHANGE
	if use_dsp:
		ssfbin[0x710:0x720] = sndcmd([0x83,0x00,effect])                 # EFFECT_CHANGE
	ssfbin[0x720:0x730] = sndcmd([0x05,0x00,0x00,volume,0x00])       # SEQUENCE_VOLUME
	ssfbin[ssoffset:ssoffset+0x10] = sndcmd([0x01,0x00,0x00,bank,track,0x00])   # SEQUENCE_START
# -----------------------------------------------------------------------------------------------------
	# Read offsets from area map
	offset = 0x500
	while offset < 0x600:
		maptype = ssfbin[offset] >> 4
		mapbank = ssfbin[offset] & 0xF
		if ssfbin[offset]==0xFF:
			break
		if mapbank == bank:
			if maptype == 0x00:
				abin = unpack('>I',ssfbin[offset:offset+4].tostring())[0] & 0x00FFFFFF
				aszbin = unpack('>I',ssfbin[offset+4:offset+8].tostring())[0] & 0x00FFFFFF
			elif maptype == 0x01:
				aseq = unpack('>I',ssfbin[offset:offset+4].tostring())[0] & 0x00FFFFFF
				aszseq = unpack('>I',ssfbin[offset+4:offset+8].tostring())[0] & 0x00FFFFFF
		if maptype == 0x02 and mapbank == effect:
			aexb = unpack('>I',ssfbin[offset:offset+4].tostring())[0] & 0x00FFFFFF
			aszexb = unpack('>I',ssfbin[offset+4:offset+8].tostring())[0] & 0x00FFFFFF
		if maptype == 0x03:
			aram = unpack('>I',ssfbin[offset:offset+4].tostring())[0] & 0x00FFFFFF
			aszram = unpack('>I',ssfbin[offset+4:offset+8].tostring())[0] & 0x00FFFFFF
			ssfbin[aram:aram+aszram] = array('B', [0x60, 0x00])*(aszram/2)
		offset += 0x8
# -----------------------------------------------------------------------------------------------------
	# Write tone data
	try:
		if szbin > aszbin:
			print 'Warning [%s - bank 0x%02X]: Tone data overflows area map.' % (nout,bank)
		ssfbin[abin:abin+szbin] = databin
	except:
		if nbin != '':
			print 'Error [%s - bank 0x%02X]: Failed to write tone data.' % (nout,bank)
# -----------------------------------------------------------------------------------------------------
	# Write sequence data
	try:
		if szseq > aszseq:
			print 'Warning [%s - bank 0x%02X]: Sequence data overflows area map.' % (nout,bank)
		ssfbin[aseq:aseq+szseq] = dataseq
	except:
		if nseq != '':
			print 'Error [%s - bank 0x%02X]: Failed to write sequence data.' % (nout,bank)
# -----------------------------------------------------------------------------------------------------
	# Write effect data
	try:
		if szexb > aszexb:
			print 'Warning [%s - bank 0x%02X]: Effect data overflows area map.' % (nout,effect)
		ssfbin[aexb:aexb+szexb] = dataexb
	except:
		if use_dsp:
			print 'Error [%s - bank 0x%02X]: Failed to write effect data.' % (nout,effect)
	if use_dsp:
		try:
			aram
			if (aram & 0x1FFF) != 0:
				print 'Error [%s - bank 0x%02X]: DSP RAM not aligned to 0x2000 offset.' % (nout,effect)
			reqram = (1 << (ssfbin[aexb+0x20]+14)) + 0x40
			if aszram < reqram:
				print 'Error [%s - bank 0x%02X]: Not enough DSP RAM to support DSP program.' % (nout,effect)
		except:
			print 'Error [%s - bank 0x%02X]: No DSP RAM found.' % (nout,effect)
# -----------------------------------------------------------------------------------------------------
	if aseq:
		ntracks = ssfbin[aseq+1]
	print '[%s - bank 0x%02X]: Sequence data contains %d track(s).' % (nout,bank,ntracks)
# -----------------------------------------------------------------------------------------------------
	# Write 2 output files
	# - ssfdata.bin contains load address and is inputted directly into bin2psf
	# - 68000ram.bin does not contain the load address and is useful for multi-pass runs of this script
	ntmp = os.path.join(os.path.dirname(nout),'temp.bin')
	nram = os.path.join(os.path.dirname(nout),'68000ram.bin')
	fo1 = open(ntmp,'wb')
	fo2 = open(nram,'wb')
	fo1.write('\x00'*4)    # load address
	fo1.write(ssfbin.tostring())
	fo2.write(ssfbin.tostring())
	fo1.close()
	fo2.close()
# -----------------------------------------------------------------------------------------------------
# Create the ssf (or ssflib/minissfs) file
	(bout,xout) = fnoext(nout)
	(btmp,xtmp) = fnoext(ntmp)
	if bout[len(xout):] == '.ssflib':
		os.system('bin2psf ssflib 17 %s 2> %s' % (ntmp,os.devnull))
		if os.access(nout,os.F_OK):
			os.remove(nout)
		os.rename('%s.ssflib' % os.path.join(os.path.dirname(nout),xtmp),nout)
		for itrack in range(0,ntracks):
			fo = open(ntmp,'wb')
			fo.write(pack('<I',0x700))
			ssfbin[ssoffset+0x3] = bank
			ssfbin[ssoffset+0x4] = itrack
			fo.write(ssfbin[0x700:0x780])
			fo.close()
			os.system('bin2psf minissf 17 %s 2> %s' % (ntmp,os.devnull))
			os.system('psfpoint "-_lib=%s" %s.minissf > %s' % (bout,os.path.join(os.path.dirname(nout),xtmp),os.devnull))
			fname = '%s_%02d_%02d.minissf' % (os.path.join(os.path.dirname(nout),xout),bank,itrack)
			if os.access(fname,os.F_OK):
				os.remove(fname)
			os.rename('%s.minissf' % os.path.join(os.path.dirname(nout),xtmp),fname)
	else:
		os.system('bin2psf ssf 17 %s 2> %s' % (ntmp,os.devnull))
		if os.access(nout,os.F_OK):
			os.remove(nout)
		os.rename('%s.ssf' % os.path.join(os.path.dirname(nout),xtmp),nout)
	return ssfbin
# =====================================================================================================

# =====================================================================================================
# Generate ssf file(s). Feel free to customize this section as you see fit (looping through a bunch of files, etc.)
ssfmake(nout,ndrv,nmap,nbin,nseq,nexb,bank,track,volume,mixerbank,mixern,effect,use_dsp)
# =====================================================================================================

# =====================================================================================================
# Update history:
# 08-10-12 (0.14) - Fixed a slight bug in zeroing-out DSP work RAM. Minor clean-ups.
# 08-05-28 (0.13) - Changed script to explicitly zero-out DSP work RAM, since older version of the
#     SDDRVS driver fail to do this. This will remove pops at the beginning of tracks.
# 07-12-20 (0.12) - Same fix as v0.11 but done in a way that actually works.
# 07-12-19 (0.11) - Fixed error that occurs when trying to print out number of tracks from a sequence bank
#     not specified in the area map.
# 07-11-22 (0.10) - Created new set of general area maps, supporting DSP program banks 1-7 and more DSP RAM
#     size options. Put in error messages for DSP RAM problems.
# 07-11-09 (0.09) - Fixed some mistakes in tone bank settings in the general area maps. Changed the ssfmake
#     function to return an array representing sound memory - sometimes useful for post-processing.
# 07-10-28 (0.08) - Changed minissf output to include all sound commands, not just the sequence bank and
#     track numbers.
# 07-10-19 (0.07) - Changed DSP RAM sizes in the area maps to account for the additional 0x40 bytes.
# 07-10-13 (0.06) - Now account for effect number when reading from area map.
# 07-10-12 (0.05) - Fixed the general area maps to handle banks 0-7 instead of just bank 0.
# 07-10-09 (0.04) - Fixed output file handling for other output directories. Cleaned up extraneous output. Gave
#     general area maps better names. Added another general area map when the DSP is not being used, 
#     providing lots of space for tone and sequence data.
# 07-10-08 (0.03) - Added ssflib/minissf support. Made the script more flexible by defining ssfmake as a 
#     function. Converted a lot of the previous struct usage to array for more speed.
# 07-10-06 (0.02) - Moved input file closing to the right place. What was there before messed up multi-pass
#     runs.
# 07-09-28 (0.01) - Added output to include number of tracks in selected sequence data. Added ability
#     to ignore data by specifying empty strings for filenames. Added dump of sound memory (without the
#     ssf load address) to support multi-pass usage.
# 07-09-25 (0.00) - Initial version.
# =====================================================================================================