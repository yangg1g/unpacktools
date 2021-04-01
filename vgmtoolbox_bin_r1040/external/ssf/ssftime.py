#=====================================================================================================
# Preliminary SSF/miniSSF auto-timer v0.07 (2007-10-12) by kingshriek
# Command-line interface script to automatically time SSF/miniSSF files
# For looping tracks, the script times 2 loops with a 10 second fade.
# Requires psfpoint (http://www.neillcorlett.com/psf/utilities.html)
# Caution: this will overwrite the length and fade tags of the specified files
# Version history located near end of file
#=====================================================================================================

#=====================================================================================================
import os
import sys
import zlib
from struct import *
from array import *
from glob import *
#=====================================================================================================

#=====================================================================================================
# loads sound memory from ssf/minissf file and associated ssflibs into an array
def ssfload(nssf):
	szpsfhdr = 0x10    # size of PSF header
	# Initialize sound memory array
	ssfbin = array('B','\x00'*0x80000)
	fssf = open(nssf,'rb')
	szssf = os.path.getsize(nssf)
	if szssf <= 0x100000:    # no ssf file should ever be above 1 MB in size
		data = fssf.read(szssf)
	else:
		data = 'invalid'    # dummy file data so that the next test fails
	fssf.close()
	# Check for valid SSF header
	if data[:0x3] != 'PSF' or data[0x3] != '\x11':
		print '%s - Error: Invalid ssf file.' % nssf
		return array('B',[1])
	offtag = unpack('<I',data[0x8:0xC])[0] + szpsfhdr
	libs = ['']*9 + [os.path.basename(nssf)]
	# Get ssflib names
	if offtag < szssf:
		tagdata = data[offtag:]
		for k in range (1,10):
			if k > 1:
				sstr = '_lib%d=' % k
			else:
				sstr = '_lib='
			offlib = tagdata.find(sstr)
			if offlib > -1:
				sztag = tagdata[offlib:].find('\x0A')
				if sztag > -1:
					libs[k-1] = tagdata[offlib+len(sstr):offlib+sztag]
	# Load ssf/minissf and any ssflibs if they exist
	for lib in libs:
		if lib != '':
			nlib = os.path.join(os.path.dirname(nssf),lib)
			flib = open(nlib, 'rb')
			hdr = flib.read(0x10)
			szlib = unpack('<I',hdr[0x8:0xC])[0]
			data = zlib.decompress(flib.read(szlib))
			szdata = len(data)
			flib.close()
			offset = unpack('<I',data[:0x4])[0]
			ssfbin[offset:offset+szdata-4] = array('B',data[0x4:])
	if len(ssfbin) > 0x80000:
		ssfbin = ssfbin[:0x80000]
	return ssfbin
#=====================================================================================================

#=====================================================================================================
# extract track data out of sound memory specified by the SEQUENCE_START command in the command area
def gettrack(ssfbin):
	# Read through host commands to get sequence bank and track number
	commandlist = ssfbin[0x700:0x780]
	for k in range(0,8):
		command = commandlist[0x10*k:0x10*k+0x10]
		if command[0] == 0x01:
			bank = command[0x3]
			track = command[0x4]
	# Look up sequence bank in area map and extract it
	areamap = ssfbin[0x500:0x600]
	for k in range(0,32):
		maptype = areamap[0x8*k] >> 4
		mapbank = areamap[0x8*k] & 0xF
		#print 'DEBUG: k=%d maptype=0x%02X mapbank=0x%02X bank=0x%02X' % (k,maptype,mapbank,bank)
		if maptype == 1 and mapbank == bank:
			offseq = unpack('>I',areamap[0x8*k:0x8*k+4])[0] & 0x00FFFFFF
			szseq = unpack('>I',areamap[0x8*k+4:0x8*k+8])[0] & 0x00FFFFFF    # not used, see comment below
			break
	seqbank = ssfbin[offseq:]    # I would use szseq here if I actually trusted the area map
	# Extract track data from sequence bank
	offtrack = unpack('>I',seqbank[4*track+2:4*track+6])[0]
	trackdata = seqbank[offtrack:]
	return trackdata
#=====================================================================================================

#=====================================================================================================
# sequence step-time accumulator
def autotime_process(trackdata, offset=0, count=100000):
	extgate = [0x200,0x800,0x1000,0x2000]    # EXT_GATE table
	extdelta = [0x100,0x200,0x800,0x1000]    # EXT_DELTA table
	steps = offset = gate = dgate = 0
	loop_events = 0
	preloopsteps = -1
	# Process all sequence events in track data, accumulating the step count
	# Not sure how consistent the Sega Saturn's sequence format is between driver versions, but
	# lets just pretend that it is
	while count > 0:
		event = trackdata[offset]
		if event < 0x80:    # NOTE
			step = (((event >> 5) & 0x1) << 8) | trackdata[offset+4]
			gate = (((event >> 6) & 0x1) << 8) | trackdata[offset+3] + dgate
			dgate = 0
			offset += 5
		elif event == 0x81:    # REFERENCE
			reference = unpack('>H',trackdata[offset+1:offset+3])[0]
			refcount = trackdata[offset+3]
			# Recursively process any nested layers of reference data
			step = autotime_process(trackdata, reference, refcount)[0]
			offset += 4
		elif event == 0x82:    # LOOP
			loop_events += 1
			step = trackdata[offset+1]
			if loop_events == 1:
				preloopsteps = steps + step
			offset += 2
			if loop_events > 1:
				step = 0    # step seems to be ignored at loop endpoint
		elif event == 0x83:    # END_OF_TRACK
			break    # end of track reached, stop processing
		elif event in range(0x88,0x8C):    # EXT_GATE
			step = 0
			dgate += extgate[event & 0x3]
			offset += 1
			count += 1    # EXT_GATE *NOT* included in REFERENCE count!
		elif event in range(0x8C,0x90):    # EXT_DELTA
			step = extdelta[event & 0x3]
			offset += 1
			count += 1    # EXT_DELTA *NOT* included in REFERENCE count!
		elif event in range(0xA0,0xC0):    # POLY_KEY_PRESSURE, CONTROL_CHANGE
			step = trackdata[offset+3]
			offset += 4
		elif event in range(0xC0,0xF0):    # PROGRAM_CHANGE, PRESSURE_CHANGE, PITCH_BEND
			step = trackdata[offset+2]
			offset += 3
		else:    # OTHER_EVENT
			step = 0
			offset += 1
		count -= 1
		steps += step
	# If the track doesn't loop, add the final gate time
	if count > 0 and loop_events == 0:
		steps += (gate + dgate)
	return (steps, preloopsteps)
#=====================================================================================================

#=====================================================================================================
# get track duration in seconds, accounting for looping and fade
def autotime(trackdata, nloops, fade):
	# Get resolution and tempo events from track data header
	resolution = unpack('>H',trackdata[0x0:0x2])[0]    # steps/quarter-note
	ntempos = unpack('>H',trackdata[0x2:0x4])[0]    # number of tempo events
	nptempos = ((unpack('>H',trackdata[0x6:0x8])[0] - 0x8))/8    # number of pre-loop tempo events
	tempodata = unpack('>'+'I'*2*ntempos,trackdata[0x8:0x8+8*ntempos])    # delta-steps / tempos
	tempostep = list(tempodata[::2])
	temposteps = sum(tempostep)
	tempo = list(tempodata[1::2])    # microseconds/quarter-note
	ptempostep = tempostep[:nptempos]
	ptemposteps = sum(ptempostep)
	ptempo = tempo[:nptempos]
	# Get track data, sans header
	offtrack = unpack('>H',trackdata[0x4:0x6])[0]
	trackdata = trackdata[offtrack:]
	# Get processed number of steps in the track data
	(steps, preloopsteps) = autotime_process(trackdata)
	# Check if processed and listed steps inconsistent, attempt to correct tempo event data that will give a blatantly wrong time
	if steps > 0 and (float(temposteps)/float(steps) > 2.0 or temposteps == 0):    # Check total step count
		#print 'DEBUG: inconsistent step counts'
		# Correct tempo event data up to actual step-counts
		cstep0 = map(lambda n: sum(tempostep[:n]), range(0,len(tempostep)+1))    # cumulative tempo steps
		cstep = filter(lambda u: u < steps, cstep0) # filter up to number of steps
		if len(cstep) < len(cstep0):
			cstep += [steps]
		else:
			cstep[-1] = steps    # if computed steps comes out lo
		tempostep = map(lambda u,v: u-v, cstep[1:], cstep[:-1])    # corrected list of tempo steps
		tempo = tempo + [tempo[-1]]
		tempo = tempo[:len(tempostep)]    # corrected list of tempos
	if preloopsteps > 0 and (float(ptemposteps)/float(preloopsteps) > 2.0 or ptemposteps == 0):    # Check pre-loop step count
		#print 'DEBUG: inconsistent pre-loop step counts'
		cstep0 = map(lambda n: sum(tempostep[:n]), range(0,len(tempostep)+1))    # cumulative tempo steps
		pcstep = filter(lambda u: u < preloopsteps, cstep0) + [preloopsteps]    # filter up to number of pre-loop steps
		ptempostep = map(lambda u,v: u-v, pcstep[1:], pcstep[:-1])    # corrected list of pre-loop tempo steps	
		ptempo = tempo[:len(ptempostep)]    # corrected list of pre-loop tempos
	# Convert from steps to minutes	
	time = sum(map(lambda u,v: float(u*v)/float(resolution)*1e-6, tempostep, tempo))
	ptime = sum(map(lambda u,v: float(u*v)/float(resolution)*1e-6, ptempostep, ptempo))
	#print 'DEBUG: steps=%d temposteps=%d' % (steps,temposteps) 
	#print 'DEBUG: preloopsteps=%d ptemposteps=%d' % (preloopsteps,ptemposteps)
	#print 'DEBUG: tempostep=%r' % tempostep
	#print 'DEBUG: tempo=%r' % tempo
	#print 'DEBUG: resolution=%d' % resolution	
	#print 'DEBUG: time=%f, ptime=%f' % (time,ptime)
	if preloopsteps > -1:    # time looped tracks to two loops, subtracting off doubly-counted pre-loop time
		time = nloops*time - (nloops - 1)*ptime
	else:    # for non-looping tracks, add 1 second
		time += 1.0
		fade = 0
	return (time, fade)
#=====================================================================================================

#=====================================================================================================
def ssftime(nsdf):
	ssfbin = ssfload(nssf)
	if len(ssfbin) == 0x80000:
		trackdata = gettrack(ssfbin)
		#fo = open('trackdata.bin','wb')    # DEBUG
		#fo.write(trackdata)    # DEBUG
		#fo.close()    # DEBUG
		(time, fadetime) = autotime(trackdata, nloops, fade)
		minutes = time // 60
		seconds = time - 60.0*minutes
		if seconds > 59.945:
			seconds = 0.0
			minutes += 1
		print 'psfpoint "-length=%d:%.1f" "-fade=%d" "%s"' % (minutes,seconds,fadetime,nssf)
		os.system('psfpoint "-length=%d:%.1f" "-fade=%d" "%s" > %s' % (minutes,seconds,fadetime,nssf,os.devnull))
	return
#=====================================================================================================

#=====================================================================================================
# ssf/minissf autotimer main function
argv = sys.argv
argc = len(argv)
nloops = 2
fade = 10
flags = {'L':0, 'f':0}
if argc < 2:
	print 'SSF/miniSSF autotimer v0.07 by kingshriek'
	print 'Requires: psfpoint  (http://www.neillcorlett.com/psf/utilities.html)'
	print 'Caution: this will overwrite the length and fade tags of the specified files'
	print 'Usage: python %s [option(s)] <ssf/minissf file(s)>' % os.path.basename(argv[0])
	print 'Options:'
	print '          -f <n>    fade time in seconds (default 10)'
	print '          -L <n>    number of loops (default 2)'
	print '          --    turn all previous flags off (resetting them to defaults)'
	print ''
	print '          Note: loop and fade settings only apply to tracks that actually loop.'
	sys.exit(0)
for arg in argv[1:]:
	for flag in flags:
		if flags[flag] != 0:
			if flag == 'L':
				nloops = int(arg)
			elif flag == 'f':
				fade = int(arg)
		flags[flag] = 0
	if arg[0] == '-':
		for flag in arg[1:]:
			if flag in flags:
				flags[flag] = 1
			elif flag == '-':
				for flag in flags:
					flags[flag] = 0
				nloops = 2
				fade = 10
			else:
				print 'Error: Invalid option -%s' % flag
				sys.exit()
	else:
		ssfs = glob(arg)
		for nssf in ssfs:
			ssftime(nssf)
#=====================================================================================================

#=====================================================================================================
# 08-10-12 (v0.07) - Fixed a bug in the reference command handling. Minor clean-ups.
# 07-12-15 (v0.06) - Added loop and fade parameters as command-line options (default values being the same as in
#     previous versions.
# 07-12-05 (v0.05) - Put in a fix for games that like to put zeros in their tempo data (Golden Axe: The Duel).
# 07-11-22 (v0.04) - Fixed a reference counting bug in the autotime_process function (EXT_GATE and EXT_DELTA are
#     not reference-counted).
# 07-11-09 (v0.03) - Fixed a minor error that sometimes caused the script to crash for extremely small tracks.
# 07-10-13 (v0.02) - Removed dependency on psf2exe and now use Python's zlib module instead. Corrected number
#     of pre-loop tempo events.
# 07-10-11 (v0.01) - Put in a better consistency check between the step number the tempo events give versus what
#     is processed by running through the sequence data.
# 07-10-09 (v0.00) - Initial release.
#=====================================================================================================