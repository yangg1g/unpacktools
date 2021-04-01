#=====================================================================================================
# SSF/miniSSF info generator v0.09 (2007-12-20) by kingshriek
# Command-line interface script that analyzes SSF/miniSSF files - useful for troubleshooting
# Example uses:
#      - checking if sequence data references any tone banks not marked as valid in (or missing from)
#            the area map
#      - checking if a suitable mixer is selected
#      - checking if the area map allocates the require amount of RAM for a DSP program
#      - checking for unused/duplicate tone banks for ssflib/minissf optimization
#      - getting information on why notes are not sounding
# Note: Tone bank data is not printed out by default due to its large volume. Run the script in 
#       verbose mode (-v) to get this info.
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
# SCSP DSP microprogram instruction class
class mpro:

	def __init__(self,data):
		self.TRA   = (data >> 56) & 0x7F
		self.TWT   = (data >> 55) & 0x1
		self.TWA   = (data >> 48) & 0x7F
		self.XSEL  = (data >> 47) & 0x1
		self.YSEL  = (data >> 45) & 0x3
		self.IRA   = (data >> 38) & 0x3F
		self.IWT   = (data >> 37) & 0x1
		self.IWA   = (data >> 32) & 0x1F
		self.TABLE = (data >> 31) & 0x1
		self.MWT   = (data >> 30) & 0x1
		self.MRD   = (data >> 29) & 0x1
		self.EWT   = (data >> 28) & 0x1
		self.EWA   = (data >> 24) & 0xF
		self.ADRL  = (data >> 23) & 0x1
		self.FRCL  = (data >> 22) & 0x1
		self.SHFT  = (data >> 20) & 0x3
		self.YRL   = (data >> 19) & 0x1
		self.NEGB  = (data >> 18) & 0x1
		self.ZERO  = (data >> 17) & 0x1
		self.BSEL  = (data >> 16) & 0x1
		self.CRA   = (data >>  9) & 0x3F
		self.NOFL  = (data >>  7) & 0x1    # not sure on this
		self.MASA  = (data >>  2) & 0x1F
		self.ADREB = (data >>  1) & 0x1
		self.NXADR = (data >>  0) & 0x1
		
	# SCSP DSP microprogram instruction dissasembler
	# Reference - Neill Corlett's AICA notes
	def dasm(self):
		input_str = ''
		if self.IRA in range(0x00,0x20):
			input_str = 'INPUT=MEMS[%d];' % (self.IRA & 0x1F)
		if self.IRA in range(0x20,0x30):
			input_str = 'INPUT=MIXS[%d];' % (self.IRA & 0x0F)
		if self.IRA in range(0x30,0x32):
			input_str = 'INPUT=EXTS[%d];' % (self.IRA & 0x01)
		
		write_str = ''
		if self.IWT:
			if self.NOFL:
				write_str = 'MEMS[%d]=NOFL(MTEMP);' % self.IWA
			else:
				write_str = 'MEMS[%d]=MTEMP;' % self.IWA
		
		if self.BSEL == 0:
			b_str = 'TEMP[%d+DEC]' % self.TRA
		if self.BSEL == 1:
			b_str = 'ACC'
		if self.ZERO:
			b_str = '0'
			
		if self.XSEL == 0:
			x_str = 'TEMP[%d+DEC]' % self.TRA
		if self.XSEL == 1:
			x_str = 'INPUT'
		
		if self.YSEL == 0:
			y_str = 'FRC'
		if self.YSEL == 1:
			y_str = 'COEF[%d]' % self.CRA
		if self.YSEL == 2:
			y_str = 'Y[23:11]'
		if self.YSEL == 3:
			y_str = 'Y[15:4]'
		
		yrl_str = ''
		if self.YRL:
			yrl_str = 'Y=INPUT;'
			
		if self.SHFT == 0:
			output_str = 'OUTPUT=SAT(ACC);'
		if self.SHFT == 1:
			output_str = 'OUTPUT=SAT(ACC*2);'
		if self.SHFT == 2:
			output_str = 'OUTPUT=ACC*2;'
		if self.SHFT == 3:
			output_str = 'OUTPUT=ACC;'
			
		acc_str = 'ACC=%s*%s' % (x_str, y_str)
		if self.ZERO:
			acc_str += ';'
		else:
			if self.NEGB:
				acc_str += '-%s;' % b_str
			else:
				acc_str += '+%s;' % b_str

		temp_str = ''
		if self.TWT:
			temp_str = 'TEMP[%d+DEC]=OUTPUT;' % self.TWA
			
		frac_str = ''
		if self.FRCL:
			if self.SHFT==3:
				frac_str = 'FRC=OUTPUT[11:0];'
			else:
				frac_str = 'FRC=OUTPUT[23:11];'
				
		mem_str = memr_str = memw_str = ''
		if self.MRD or self.MWT:
			mem_str = 'MADRS[%d]' % self.MASA
			if not self.TABLE:
				mem_str += '+DEC'
			if self.ADREB:
				mem_str += '+ADRS'
			if self.NXADR:
				mem_str += '+1'
		if self.MRD:
			memr_str = 'MTEMP=RB[%s];' % mem_str
		if self.MWT:
			if self.NOFL:
				memw_str = 'RB[%s]=NOFL(OUTPUT);' % mem_str
			else:
				memw_str = 'RB[%s]=OUTPUT;' % mem_str
		
		addr_str = ''
		if self.ADRL:
			if self.SHFT == 3:
				addr_str = 'ADRS=OUTPUT[23:12];'
			else:
				addr_str = 'ADRS=INPUT[23:16];'
				
		efct_str = ''
		if self.EWT:
			efct_str = 'EFREG[%d]=OUTPUT;' % self.EWA

		dasm_str = '%s %s %s %s %s %s %s %s %s %s %s' % \
		(input_str, output_str, acc_str, write_str, yrl_str, temp_str, frac_str, memr_str, memw_str, addr_str, efct_str)
		
		if dasm_str.find('INPUT', dasm_str.find('INPUT')+1) < 0:
			input_str = ''
		if dasm_str.find('OUTPUT', dasm_str.find('OUTPUT')+1) < 0:
			output_str = ''
			
		dasm_str = '%s %s %s %s %s %s %s %s %s %s %s' % \
		(input_str, output_str, acc_str, write_str, yrl_str, temp_str, frac_str, memr_str, memw_str, addr_str, efct_str)
		
		dasm_list = dasm_str.split()
		dasm_str = ''
		for idx in range(0,len(dasm_list[:-1])):
			dasm_list[idx] += ' '
		dasm_str = ''.join(dasm_list)
		return dasm_str
#=====================================================================================================

#=====================================================================================================
# loads sound memory from ssf/minissf file and associated ssflibs into an array
def ssfload(nssf):
	szpsfhdr = 0x10    # size of PSF header
	# Initialize sound memory array
	ssfbin = array('B',[0]*0x80000)
	fssf = open(nssf,'rb')
	szssf = os.path.getsize(nssf)
	if szssf <= 0x100000:    # no ssf file should ever be above 1 MB in size
		data = fssf.read(szssf)
	else:
		data = 'invalid'    # dummy file data so that the next test fails
	fssf.close()
	# Check for valid SSF header
	if data[:0x3] != 'PSF' or data[0x3] != '\x11':
		print '======================================================================================'
		print '%s - Error: Invalid ssf file.' % nssf
		print '======================================================================================'
		print '\n'
		return array('B',[1])
	offtag = unpack('<I',data[0x8:0xC])[0] + szpsfhdr
	libs = ['']*9 + [os.path.basename(nssf)]
	# Get ssflib names
	tagdata = ''
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
	print '=========================================================================================='
	print 'File Info'
	print '------------------------------------------------------------------------------------------'
	for lib in libs[::-1]:
		if lib != '':
			szlib = os.path.getsize(os.path.join(os.path.dirname(nssf),lib))
			flib = open(os.path.join(os.path.dirname(nssf),lib),'rb')
			flib.seek(0xC)
			crcdata = flib.read(4)
			crc32 = unpack('<I', crcdata)[0]
			flib.close()
			print '%s - %d bytes (%08X)' % (lib, szlib, crc32)
	print '=========================================================================================='
	print '\n'
	print '=========================================================================================='
	print 'Tag Data'
	print '------------------------------------------------------------------------------------------'
	if tagdata != '':
		print '%s' % tagdata[5:]
	print '=========================================================================================='
	print '\n'
	if len(ssfbin) > 0x80000:
		ssfbin = ssfbin[:0x80000]
	return ssfbin
#=====================================================================================================

#=====================================================================================================
def getareamap(ssfbin):
	areamap = ssfbin[0x500:0x600]
	areamap_end = 0
	while areamap_end < 0x100:
		if areamap[areamap_end] == 0xFF:
			break
		areamap_end += 0x8
	return areamap[:areamap_end]
#=====================================================================================================

#=====================================================================================================
def gethostcommands(ssfbin):
	seqbank = seqtrack = effectbank = mixerbank = mixer_id = None
	hostcommands = ssfbin[0x700:0x780]
	offset = 0
	while offset < 0x80:
		command_block = hostcommands[offset:offset+0x10]
		command_id = command_block[0]
		if command_id == 0x01:    # SEQUENCE_START
			seqbank = command_block[3]
			seqtrack = command_block[4]
		elif command_id == 0x83:    # EFFECT_CHANGE
			effectbank = command_block[2]
		elif command_id == 0x87:    # MIXER_CHANGE
			mixerbank = command_block[2]
			mixer_id = command_block[3]
		offset += 0x10
	return (hostcommands, seqbank, seqtrack, effectbank, mixerbank, mixer_id)
#=====================================================================================================

#=====================================================================================================
def getbank(ssfbin, type_id, bank_id):
	areamap = getareamap(ssfbin)
	offset = 0
	ok = 0
	bankdata = None
	while offset < len(areamap):
		areablock = areamap[offset:offset+0x8]
		type = areablock[0] >> 4
		bank = areablock[0] & 0xF
		transfer_complete = areablock[4] >> 7
		if transfer_complete and type_id == type and bank_id == bank:
			data_offset = unpack('>I', areablock[0x0:0x4])[0] & 0x00FFFFFF
			data_size = unpack('>I', areablock[0x4:0x8])[0] & 0x00FFFFFF
			bankdata = ssfbin[data_offset:data_offset+data_size]
			ok = 1
			break
		offset += 0x8
	return (bankdata, ok)
#=====================================================================================================

#=====================================================================================================
def testtonebank(tonebank):
	try:
		ok = 0
		mixer_offset = unpack('>H', tonebank[0x0:0x2])[0]
		velocity_offset = unpack('>H', tonebank[0x2:0x4])[0]
		peg_offset = unpack('>H', tonebank[0x4:0x6])[0]
		plfo_offset = unpack('>H', tonebank[0x6:0x8])[0]
		if mixer_offset >= 0x000A and mixer_offset < 0x20A:
			nvoices = (mixer_offset - 8)/2
			voice_offsets = unpack('>'+'H'*nvoices,tonebank[0x8:0x8+2*nvoices])
			offset_list = (mixer_offset, velocity_offset, peg_offset, plfo_offset) + voice_offsets
			offset_diff = map(lambda x,y:x-y,offset_list[1:],offset_list[:-1])
			monotonic_sequence = (filter(lambda x:x>0,offset_diff) == offset_diff)
			deltas_consistent = (map(lambda x,y:x%y,offset_diff,[0x12,0x0A,0x0A,0x04] + [0x20]*(nvoices-1)) == [0x00,0x00,0x00,0x00] + [0x4]*(nvoices-1))
			if monotonic_sequence and deltas_consistent:
				ok = 1
		return ok
	except:
		return 0
#=====================================================================================================

#=====================================================================================================
def testsequencebank(sequencebank):
	try:
		ok = 0
		ntracks = unpack('>H',sequencebank[0x0:0x2])[0]
		trackblock_offset = unpack('>I',sequencebank[0x2:0x6])[0]
		if ntracks > 0 and ntracks < 128 and 4*ntracks+2 == trackblock_offset:
			trackblock = gettrackblock(sequencebank,0)
			ntempos = unpack('>H',trackblock[0x2:0x4])[0]
			trackdata_offset = unpack('>H',trackblock[0x4:0x6])[0]
			if 8*ntempos + 0x8 == trackdata_offset:
				ok = 1
		return ok
	except:
		return 0
#=====================================================================================================

#=====================================================================================================
def testdspbank(dspbank):
	try:
		ok = 0
		name = dspbank[0x0:0x20].tostring().replace('\x00',' ').strip()
		if name.upper().find('.EX') >= 0:
			ok = 1
		return ok
	except:
		return 0
#=====================================================================================================

#=====================================================================================================
def testdspram(dspbank, map_offset, map_size):
	try:
		ok = 0
		rbl = dspbank[0x20] & 0x3    # Ring buffer length type
		ntables = dspbank[0x21]    # Number of COEF tables
		mem_req = 0x4000*(1 << rbl) + 0xA00*ntables + 0x40
		if map_offset & 0x1FFF == 0 and map_size <= 0x20040 and map_size >= mem_req:
			ok = 1
		return ok
	except:
		return 0
#=====================================================================================================

#=====================================================================================================
def testbank(data, type_id, map_offset, map_size):
	if type_id == 0:
		return testtonebank(data)
	elif type_id == 1:
		return testsequencebank(data)
	elif type_id == 2:
		return testdspbank(data)
	elif type_id == 3:
		return testdspram(data, map_offset, map_size)
	else:
		return 1
#=====================================================================================================

#=====================================================================================================
def gettonebank(ssfbin, bank_id):
	(tonebank, ok) = getbank(ssfbin, 0, bank_id)
	if ok:
		ok = testtonebank(tonebank)
	return (tonebank, ok)
#=====================================================================================================

#=====================================================================================================
def getsequencebank(ssfbin, bank_id):
	(sequencebank, ok) = getbank(ssfbin, 1, bank_id)
	if ok:
		ok = testsequencebank(sequencebank)
	return (sequencebank, ok)
#=====================================================================================================

#=====================================================================================================
def getdspbank(ssfbin, bank_id):
	(dspbank, ok) = getbank(ssfbin, 2, bank_id)
	if ok:
		ok = testdspbank(dspbank)
	return (dspbank, ok)
#=====================================================================================================

#=====================================================================================================
def getmixer(tonebank, mixer_id):
	mixer_offset = unpack('>H', tonebank[0x0:0x2])[0]
	mixer = tonebank[mixer_offset+0x12*mixer_id:mixer_offset+0x12*mixer_id+0x12]
	return mixer
#=====================================================================================================

#=====================================================================================================
def getvelocity(tonebank, velocity_id):
	velocity_offset = unpack('>H', tonebank[0x2:0x4])[0]
	velocity = tonebank[velocity_offset+0xA*velocity_id:velocity_offset+0xA*velocity_id+0xA]
	return velocity
#=====================================================================================================

#=====================================================================================================
def getpitchenvelope(tonebank, peg_id):
	peg_offset = unpack('>H', tonebank[0x4:0x6])[0]
	pitchenvelope = tonebank[peg_offset+0xA*peg_id:peg_offset+0xA*peg_id+0xA]
	return pitchenvelope
#=====================================================================================================

#=====================================================================================================
def getpitchlfo(tonebank, plfo_id):
	plfo_offset = unpack('>H', tonebank[0x6:0x8])[0]
	pitchlfo = tonebank[plfo_offset+0x4*plfo_id:plfo_offset+0x4*plfo_id+0x4]
	return pitchlfo
#=====================================================================================================

#=====================================================================================================
def getvoice(tonebank, voice_id):
	voice_offset = unpack('>H', tonebank[0x8+2*voice_id:0x8+2*voice_id+0x2])[0]
	nlayers = unpack('b', tonebank[voice_offset+0x2:voice_offset+0x3])[0] + 1
	voice = tonebank[voice_offset:voice_offset+0x20*nlayers + 0x4]
	return voice
#=====================================================================================================

#=====================================================================================================
def getlayer(voice, layer_id):
	layer = voice[0x4+0x20*layer_id:0x4+0x20*layer_id+0x20]
	return layer
#=====================================================================================================

#=====================================================================================================
def gettrackblock(sequencebank, track_id):
	ntracks = unpack('>H', sequencebank[0x0:0x2])[0]
	if track_id < ntracks:
		block_offset = unpack('>I', sequencebank[4*track_id+2:4*track_id+6])[0]
		trackblock = sequencebank[block_offset:]
	return trackblock
#=====================================================================================================

#=====================================================================================================
def gettrackdata(trackblock):
	data_offset = unpack('>H', trackblock[0x4:0x6])[0]
	trackdata = trackblock[data_offset:]
	return trackdata
#=====================================================================================================

#=====================================================================================================
def printtrackdata(trackdata):
	channel_banks = [None]*16
	channel_voices = [None]*16
	offset = 0
	bank_list = set([])
	voice_list = [set([]),set([]),set([]),set([]),set([]),set([]),set([]),set([]),
	              set([]),set([]),set([]),set([]),set([]),set([]),set([]),set([])]
	gate_table = [ 0x200, 0x800, 0x1000, 0x2000]
	delta_table = [ 0x100, 0x200, 0x800, 0x1000]
	note_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
	ctrl_list = { 0x01: 'MODULATION_WHEEL ', 0x02: 'EXPRESSION       ', 0x07: 'MAIN_VOLUME      ',
	              0x0A: 'DIRECT_PAN       ', 0x0B: 'EXPRESSION       ', 0x10: 'MIXER_CHANGE     ',
				  0x11: 'EFFECT_PAN       ', 0x20: 'TONE_BANK        ', 0x40: 'DAMPER           ',
				  0x46: 'EFFECT_PAN       ', 0x47: 'EFFECT_RETURN    ', 0x50: 'QSOUND_POSITION  ',
				  0x51: '3D_DISTANCE      ', 0x52: '3D_AZIMUTH       ', 0x53: '3D_ELEVATION     ',
				  0x5B: 'EFFECT_CHANGE    ', 0x78: 'ALL_SOUND_OFF    ', 0x7B: 'ALL_NOTE_OFF     '}
	cstep = 0
	while offset < len(trackdata):
		event = trackdata[offset]
		if event < 0x80:    # NOTE
			channel = event & 0x0F
			key = trackdata[offset+1]
			note = note_list[key%12]
			octave = key//12 - 1
			volume = trackdata[offset+2]
			gate = (((event >> 6) & 0x1) << 8) | trackdata[offset+3]
			step = (((event >> 5) & 0x1) << 8) | trackdata[offset+4]
			print '[0x%05X] %02X %02X %02X %02X %02X  NOTE              : channel=%d note=%s(%d) key=%d volume=%d gate=%d step=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],trackdata[offset+2],trackdata[offset+3],trackdata[offset+4],channel,note,octave,key,volume,gate,step)
			offset += 5
		elif event == 0x81:    # REFERENCE
			roffset = unpack('>H',trackdata[offset+1:offset+3])[0]
			rlength = trackdata[offset+3]
			print '[0x%05X] %02X %02X %02X %02X     REFERENCE         : offset=0x%04X length=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],trackdata[offset+2],trackdata[offset+3],roffset,rlength)
			offset += 4
		elif event == 0x82:    # LOOP
			step = trackdata[offset+1]
			print '[0x%05X] %02X %02X           LOOP              : step=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],step)
			offset += 2
		elif event == 0x83:    # END_OF_TRACK
			print '[0x%05X] %02X              END_OF_TRACK      : ' % \
			(offset,trackdata[offset])
			break
		elif event in range(0x88,0x8C):    # EXT_GATE
			gate = gate_table[event&0x3]
			print '[0x%05X] %02X              EXT_GATE          : gate=%d' % \
			(offset,trackdata[offset],gate)
			offset += 1
		elif event in range(0x8C,0x90):    # EXT_DELTA
			delta = delta_table[event&0x3]
			print '[0x%05X] %02X              EXT_DELTA         : delta=%d' % \
			(offset,trackdata[offset],delta)
			offset += 1
		elif event in range(0xA0,0xB0):    # POLY_KEY_PRESSURE
			channel = event & 0xF
			key = trackdata[offset+1]
			value = trackdata[offset+2]
			step = trackdata[offset+3]
			print '[0x%05X] %02X %02X %02X %02X     POLY_KEY_PRESSURE : channel=%d key=%d value=%d step=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],trackdata[offset+2],trackdata[offset+3],channel,key,value,step)
			offset += 4
		elif event in range(0xB0,0xC0):    # CONTROL_CHANGE
			channel = event & 0xF
			ctrl_val = trackdata[offset+1]
			if ctrl_val == 0x20:    # BANK_SELECT
				bank = trackdata[offset+2] & 0xF
				channel_banks[channel] = bank
			if ctrl_val in ctrl_list:
				control = ctrl_list[ctrl_val]
			else:
				control = 'OTHER_CONTROL    '
			value = trackdata[offset+2]
			step = trackdata[offset+3]
			print '[0x%05X] %02X %02X %02X %02X     %s : channel=%d value=%d step=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],trackdata[offset+2],trackdata[offset+3],control,channel,value,step)
			offset += 4
		elif event in range(0xC0,0xD0):    # PROGRAM_CHANGE
			channel = event & 0xF
			voice = trackdata[offset+1]
			step = trackdata[offset+2]
			if channel_banks[channel] != None:
				bank_list.add(channel_banks[channel])
				voice_list[channel_banks[channel]].add(channel_voices[channel])
			print '[0x%05X] %02X %02X %02X        PROGRAM_CHANGE    : channel=%d voice=%d step=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],trackdata[offset+2],channel,voice,step)
			offset += 3
		elif event in range(0xD0,0xE0):    # CHANNEL_PRESSURE
			channel = event & 0xF
			value = trackdata[offset+1]
			step = trackdata[offset+2]
			print '[0x%05X] %02X %02X %02X        CHANNEL_PRESSURE  : channel=%d value=%d step=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],trackdata[offset+2],channel,value,step)
			offset += 3
		elif event in range(0xE0,0xF0):    # PITCH_BEND
			channel = event & 0xF
			value = trackdata[offset+1]
			step = trackdata[offset+2]
			print '[0x%05X] %02X %02X %02X        PITCH_BEND        : channel=%d value=%d step=%d' % \
			(offset,trackdata[offset],trackdata[offset+1],trackdata[offset+2],channel,value,step)
			offset += 3
		else:    # OTHER_EVENT
			print '[0x%05X] %02X              OTHER_EVENT       : ' % \
			(offset,trackdata[offset])
			offset += 1
	return (bank_list, voice_list)
#=====================================================================================================

#=====================================================================================================
def printtrackvoices(trackdata):
	channel_banks = [None]*16
	channel_voices = [None]*16
	offset = 0
	bank_list = set([])
	voice_list = [set([]),set([]),set([]),set([]),set([]),set([]),set([]),set([]),
	              set([]),set([]),set([]),set([]),set([]),set([]),set([]),set([])]
	while offset < len(trackdata):
		event = trackdata[offset]
		if event < 0x80:    # NOTE
			offset += 5
		elif event == 0x81:    # REFERENCE
			offset += 4
		elif event == 0x82:    # LOOP
			offset += 2
		elif event == 0x83:    # END_OF_TRACK
			break
		elif event in range(0xA0,0xB0):    # POLY_KEY_PRESSURE
			offset += 4
		elif event in range(0xB0,0xC0):    # CONTROL_CHANGE
			control = trackdata[offset+1]
			if control == 0x20:    # BANK_SELECT
				channel = event & 0xF
				bank = trackdata[offset+2] & 0xF
				channel_banks[channel] = bank
			offset += 4
		elif event in range(0xC0,0xD0):    # PROGRAM_CHANGE
			channel = event & 0xF
			voice = trackdata[offset+1]
			channel_voices[channel] = voice
			if channel_banks[channel] != None:
				print 'Channel %2d: Bank %2d, Voice %3d' % (channel, channel_banks[channel], channel_voices[channel])
				bank_list.add(channel_banks[channel])
				voice_list[channel_banks[channel]].add(channel_voices[channel])
			offset += 3
		elif event in range(0xD0,0xF0):    # CHANNEL_PRESSURE, PITCH_BEND
			offset += 3
		else:    # EXT_GATE, EXT_DELTA, OTHER_EVENT
			offset += 1
	return (bank_list, voice_list)
#=====================================================================================================

#=====================================================================================================
def printdriverversion(ssfbin):
	print '=========================================================================================='
	print 'Driver Version'
	print '------------------------------------------------------------------------------------------'
	offset = 0x1000
	startblock = ssfbin[offset:offset+0x100:2]
	bra_index = startblock.index(0x60)
	startblock = ssfbin[offset:offset+0x100]
	if bra_index >= 0:
		rel_offset = startblock[2*bra_index+1]
		version_start = 2*bra_index + 2
		version_end = version_start + rel_offset
		if rel_offset == 0:
			rel_offset = unpack('>H',startblock[2*bra_index+2:2*bra_index+4])[0]
			version_start = 2*bra_index + 4
			version_end = version_start + rel_offset - 2
		driverversion = startblock[version_start:version_end].tostring()
		version_offset = 0
		while version_offset < len(driverversion):
			print '%s' % driverversion[version_offset:version_offset+0x10].replace('\x00',' ')
			version_offset += 0x10
	else:
		print 'Unable to get driver version info.'
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printareamap(ssfbin, areamap):
	print '=========================================================================================='
	print 'Area Map (0x500-0x5FF)'
	print '------------------------------------------------------------------------------------------'
	offset = 0
	type_list = {0:'TONE', 1:'SEQUENCE', 2:'DSP_PROGRAM', 3:'DSP_RAM'}
	while offset < len(areamap):
		areablock = areamap[offset:offset+0x8]
		type_id = areablock[0] >> 4
		if type_id in type_list:
			type = type_list[type_id]
		else:
			type = 'UNKNOWN (%d)' % type_id
		bank = areablock[0] & 0xF
		data_offset = unpack('>I', areablock[0x0:0x4])[0] & 0x00FFFFFF
		transfer_complete = areablock[4] >> 7
		data_size = unpack('>I', areablock[0x4:0x8])[0] & 0x00FFFFFF
		pad = ' '*(12 - len(type))
		if type_id == 3:
			(data, ok) = getdspbank(ssfbin, bank)
			if ok:
				valid = testbank(data, type_id, data_offset, data_size)
			else:
				valid = 0
		else:
			data = ssfbin[data_offset:data_offset+data_size]
			valid = testbank(data, type_id, data_offset, data_size)
		if valid and type_id != 3:
			crc32 = unpack('I',pack('i',zlib.crc32(data)))[0]
			print '%s %s Bank %2d : offset=0x%05X size=0x%05X transferred=%d valid=%d crc32=0x%08X' % (type, pad, bank, data_offset, data_size, transfer_complete, valid, crc32)
		else:
			print '%s %s Bank %2d : offset=0x%05X size=0x%05X transferred=%d valid=%d' % (type, pad, bank, data_offset, data_size, transfer_complete, valid)
		offset += 0x8
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printhostcommands(hostcommands):
	print '=========================================================================================='
	print 'Host Commands (0x700-0x77F)'
	print '------------------------------------------------------------------------------------------'
	offset = 0
	command_list = { 0x01:'SEQUENCE_START'     , 0x02:'SEQUENCE_STOP'       , 0x03:'SEQUENCE_PAUSE'        , 
	                 0x04:'SEQUENCE_CONTINUE'  , 0x05:'SEQUENCE_VOLUME'     , 0x07:'TEMPO_CHANGE'          , 
					 0x08:'MAP_CHANGE'         , 0x09:'MIDI_DIRECT_CONTROL' , 0x0A:'VOLUME_ANALYZE_START'  ,
					 0x0B:'VOLUME_ANALYZE_STOP', 0x0C:'DSP_STOP'            , 0x0D:'SOUND_ALL_OFF'         ,
					 0x0E:'SEQUENCE_PAN'       , 0x10:'SOUND_INITIAL'       , 0x11:'3D_CONTROL'            ,
					 0x12:'QSOUND_CONTROL'     , 0x80:'CDDA_LEVEL'          , 0x81:'CDDA_PAN'              ,
					 0x82:'TOTAL_VOLUME'       , 0x83:'EFFECT_CHANGE'       , 0x85:'PCM_START'             ,
					 0x86:'PCM_STOP'           , 0x87:'MIXER_CHANGE'        , 0x88:'MIXER_PARAMETER_CHANGE',
					 0x89:'HARD_CHECK'         , 0x8A:'PCM_PARAMETER_CHANGE'                                  }
	hard_check_list = { 0x00:'DRAM_4MB_R/W',              0x01:'DRAM_8MB_R/W'           , 0x02:'SCSP_MIDI',
	                    0x03:'SOUND_SOURCE_OUTPUT_(L/R)', 0x04:'SOUND_SOURCE_OUTPUT_(L)', 0x05: 'SOUND_SOURCE_OUTPUT_(L)' } 
	while offset < len(hostcommands):
		command_block = hostcommands[offset:offset+0x10]
		command_id = command_block[0]
		if command_id != 0x00 and command_id != 0xFF:
			if command_id in command_list:
				command = command_list[command_id]
			else:
				command = 'UNKNOWN_COMMAND'
			pad = ' '*(23 - len(command))
			if command_id == 0x01:    # SEQUENCE_START
				control = command_block[2] & 0x07
				bank = command_block[3] & 0x0F
				track = command_block[4] & 0x7F
				priority = command_block[5] & 0x1F
				print '%s (0x%02X) %s: control=%d bank=%d track=%d priority=%d' % \
				(command, command_id, pad, control, bank, track, priority)
			elif command_id == 0x02:    # SEQUENCE_STOP
				control = command_block[2] & 0x07
				print '%s (0x%02X) %s: control=%d' % \
				(command, command_id, pad, control)
			elif command_id == 0x03:    # SEQUENCE_PAUSE
				control = command_block[2] & 0x07
				print '%s (0x%02X) %s: control=%d' % \
				(command, command_id, pad, control)
			elif command_id == 0x04:    # SEQUENCE_CONTINUE
				control = command_block[2] & 0x07
				print '%s (0x%02X) %s: control=%d' % \
				(command, command_id, pad, control)
			elif command_id == 0x05:    # SEQUENCE_VOLUME
				control = command_block[2] & 0x07
				volume = command_block[3] & 0x7F
				fade = command_block[4]
				print '%s (0x%02X) %s: control=%d volume=%d fade=%d' % \
				(command, command_id, pad, control, volume, fade)
			elif command_id == 0x07:    # TEMPO_CHANGE
				control = command_block[2] & 0x07
				tempo = unpack('>h', command_block[4:6])[0]
				print '%s (0x%02X) %s: control=%d tempo=%+d' % \
				(command, command_id, pad, control, tempo)
			elif command_id == 0x08:    # MAP_CHANGE
				areamap = command_block[2]
				print '%s (0x%02X) %s: areamap=%d' % \
				(command, command_id, pad, areamap)
			elif command_id == 0x09:    # MIDI_DIRECT_CONTROL
				midi_command = command_block[2]
				midi_channel = command_block[3]
				midi_data1 = command_block[4] & 0x7F
				midi_data2 = command_block[5] & 0x7F
				print '%s (0x%02X) %s: midi_command=0x%02X midi_channel=%d midi_data1=0x%02X midi_data2=0x%02X' % \
				(command, command_id, pad, midi_command, midi_channel, midi_data1, midi_data2)
			elif command_id == 0x0A:    # VOLUME_ANALYZE_START
				print '%s (0x%02X) %s:' % \
				(command, command_id, pad)
			elif command_id == 0x0B:    # VOLUME_ANALYZE_STOP
				print '%s (0x%02X) %s:' % \
				(command, command_id, pad)
			elif command_id == 0x0C:    # DSP_STOP
				print '%s (0x%02X) %s:' % \
				(command, command_id, pad)
			elif command_id == 0x0D:    # SOUND_ALL_OFF
				print '%s (0x%02X) %s:' % \
				(command, command_id, pad)
			elif command_id == 0x0E:    # SEQUENCE_PAN
				control = command_block[2]
				pan_control = command_block[3] >> 7
				midi_pan = command_block[3] & 0x7F
				print '%s (0x%02X) %s: control=%d pan_control=%d midi_pan=%d' % \
				(command, command_id, pad, control, pan_control, midi_pan)
			elif command_id == 0x10:    # SOUND_INITIAL
				stop_seq = command_block[2] & 0x01
				stop_pcm = command_block[3] & 0x01
				stop_cdda = command_block[4] & 0x01
				init_dsp = command_block[5] & 0x01
				init_mixer = command_block[6] & 0x01
				print '%s (0x%02X) %s: stop_seq=%d stop_pcm=%d stop_cdda=%d init_dsp=%d init_mixer=%d' % \
				(command, command_id, pad, stop_seq, stop_pcm, stop_cdda, init_dsp, init_mixer)
			elif command_id == 0x11:    # 3D_CONTROL
				channel = command_block[2] & 0x01
				distance = command_block[3] & 0x7F
				azimuth = command_block[4] & 0x7F
				elevation = command_block[5] & 0x7F
				print '%s (0x%02X) %s: channel=%d distance=%d azimuth=%d elevation=%d' % \
				(command, command_id, pad, channel, distance, azimuth, elevation)
			elif command_id == 0x12:    # QSOUND_CONTROL
				channel = command_block[2] & 0x7
				pan_position = command_block[3] & 0x1F
				print '%s (0x%02X) %s: channel=%d pan_position=%d' % \
				(command, command_id, pad, channel, pan_position)
			elif command_id == 0x80:    # CDDA_LEVEL
				cdda_level_left = command_block[2]
				cdda_level_right = command_block[3]
				print '%s (0x%02X) %s: cdda_level_left=%d cdda_level_right=%d' % \
				(command, command_id, pad, cdda_level_left, cdda_level_right)
			elif command_id == 0x81:    # CDDA_PAN
				cdda_pan_left = command_block[2] & 0x1F
				cdda_pan_right = command_block[3] & 0x1F
				print '%s (0x%02X) %s: cdda_pan_left=%d, cdda_pan_right=%d' % \
				(command, command_id, pad, cdda_pan_left, cdda_pan_right)
			elif command_id == 0x82:    # TOTAL_VOLUME
				total_volume = command_block[2] & 0x0F
				print '%s (0x%02X) %s: total_volume=%d' % \
				(command, command_id, pad, total_volume)
			elif command_id == 0x83:    # EFFECT_CHANGE
				effect = command_block[2] & 0x0F
				print '%s (0x%02X) %s: effect=%d' % \
				(command, command_id, pad, effect)
			elif command_id == 0x85:    # PCM_START
				stereo = command_block[2] >> 7
				pcm8b = (command_block[2] >> 4) & 0x1
				stream = command_block[2] & 0x0F
				direct_level = command_block[3] >> 5
				direct_pan = command_block[3] & 0x1F
				address = unpack('>H', command_block[4:5])[0] << 4
				size = unpack('>H', command_block[6:7])[0]
				pitch = unpack('>H', command_block[8:9])[0]
				effect_channel_right = command_block[10] >> 3
				effect_level_right = command_block[10] & 0x07
				effect_channel_left = command_block[11] >> 3
				effect_level_left = command_block[11] & 0x07
				print '%s (0x%02X) %s: stereo=%d pcm8b=%d stream=%d direct_level=%d direct_pan=%d address=0x%05X size=0x%4X pitch=%d effect_channel_right=%d effect_level_right=%d effect_channel_left=%d effect_level_left=%d' % \
				(command, command_id, pad, stereo, pcm8b, stream, direct_level, direct_pan, address, size, pitch, effect_channel_right, effect_level_right, effect_channel_left, effect_level_left)
			elif command_id == 0x86:    # PCM_STOP
				stream = command_block[2] & 0x07
				print '%s (0x%02X) %s: stream=%d' % \
				(command, command_id, pad, stream)
			elif command_id == 0x87:    # MIXER_CHANGE
				mixerbank = command_block[2] & 0x0F
				mixernumber = command_block[3] & 0x7F
				print '%s (0x%02X) %s: mixerbank=%d mixernumber=%d' % \
				(command, command_id, pad, mixerbank, mixernumber)
			elif command_id == 0x88:    # MIXER_PARAMETER_CHANGE
				effect_channel = command_block[2] & 0x1F
				effect_level = command_block[3] >> 5
				effect_pan = command_block[3] & 0x1F
				print '%s (0x%02X) %s: effect_channel=%d effect_level=%d effect_pan=%d' % \
				(command, command_id, pad, effect_channel, effect_level, effect_pan)
			elif command_id == 0x89:    # HARD_CHECK
				check_id = command_block[2]
				if check_id in hard_check_list:
					check = hard_check_list[check_id]
				else:
					check = 'UNKNOWN_CHECK'
				print '%s (0x%02X) %s: check=%s' % \
				(command, command_id, pad, check)
			elif command_id == 0x8A:    # PCM_PARAMTER_CHANGE
				stream = command_block[2] & 0x07
				direct_level = command_block[3] >> 5
				direct_pan = command_block[3] & 0x1F
				pitch = unpack('>H', command_block[8:9])[0]
				effect_channel_right = command_block[10] >> 3
				effect_level_right = command_block[10] & 0x07
				effect_channel_left = command_block[11] >> 3
				effect_level_left = command_block[11] & 0x07
				print '%s (0x%02X) %s: stream=%d direct_level=%d direct_pan=%d pitch=%d effect_channel_right=%d effect_level_right=%d effect_channel_left=%d effect_level_left=%d' % \
				(command, command_id, pad, stream, direct_level, direct_pan, pitch, effect_channel_right, effect_level_right, effect_channel_left, effect_level_left)
			else:    # UNKNOWN_COMMAND
				print '%s (0x%02X) %s: P=[0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X]' % \
				((command, command_id, pad) + tuple(command_block[0x2:0xE].tolist()))
		offset += 0x10
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printmixer(mixer, bank_id, mixer_id):
	print '=========================================================================================='
	print 'Tone Bank %d - Mixer %d' % (bank_id, mixer_id)
	print '------------------------------------------------------------------------------------------'
	for slot in range(0,0x12):
		EFSDL = mixer[slot] >> 5    # EFFECT_SEND
		EFPAN = mixer[slot] & 0x1F    # EFFECT_PAN
		if slot < 0x10:
			print 'Effect out %2d: EFSDL=%1d EFPAN=%2d' % (slot & 0xF, EFSDL, EFPAN)
		else:
			print 'CDDA effect %1d: EFSDL=%1d EFPAN=%2d' % (slot & 0xF, EFSDL, EFPAN)
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printvelocity(velocity, bank_id, velocity_id):
	print '=========================================================================================='
	print 'Tone Bank %d - Velocity %d' % (bank_id, velocity_id)
	print '------------------------------------------------------------------------------------------'
	slope0    = unpack('b',velocity[0:1])[0]; point0    = velocity[1]; level0    = velocity[2]
	slope1    = unpack('b',velocity[3:4])[0]; point1    = velocity[4]; level1    = velocity[5]
	slope2    = unpack('b',velocity[6:7])[0]; point2    = velocity[7]; level2    = velocity[8]
	slope3    = unpack('b',velocity[9:10])[0]
	print 'Velocity range 0: slope=%3d point=%3d level=%3d' % (slope0, point0, level0)
	print 'Velocity range 1: slope=%3d point=%3d level=%3d' % (slope1, point1, level1)
	print 'Velocity range 2: slope=%3d point=%3d level=%3d' % (slope2, point2, level2)
	print 'Velocity range 3: slope=%3d' % slope3
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printpitchenvelope(pitchenvelope, bank_id, peg_id):
	print '=========================================================================================='
	print 'Tone Bank %d - Pitch Envelope (PEG) %d' % (bank_id, peg_id)
	print '------------------------------------------------------------------------------------------'
	PEG_DLY = pitchenvelope[0]; OL = unpack('b',pitchenvelope[1:2])[0]    # DELAY, OFFSET
	AR = unpack('b',pitchenvelope[2:3])[0]; AL = unpack('b',pitchenvelope[3:4])[0]    # ATTACK
	DR = unpack('b',pitchenvelope[4:5])[0]; DL = unpack('b',pitchenvelope[5:6])[0]    # DECAY
	SR = unpack('b',pitchenvelope[6:7])[0]; SL = unpack('b',pitchenvelope[7:8])[0]    # RELASE
	RR = unpack('b',pitchenvelope[8:9])[0]; RL = unpack('b',pitchenvelope[9:10])[0]   # SUSTAIN
	print 'INIT   : delay=%4d  offset=%4d' % (PEG_DLY, OL)
	print 'ATTACK : rate =%4d  level =%4d' % (AR, AL)
	print 'DECAY  : rate =%4d  level =%4d' % (DR, DL)
	print 'SUSTAIN: rate =%4d  level =%4d' % (SR, SL)
	print 'RELEASE: rate =%4d  level =%4d' % (RR, RL)
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printpitchlfo(pitchlfo, bank_id, plfo_id):
	print '=========================================================================================='
	print 'Tone Bank %d - Pitch LFO (PLFO) %d' % (bank_id, plfo_id)
	print '------------------------------------------------------------------------------------------'
	DLY = pitchlfo[0]; FRQR = pitchlfo[1]
	HT  = pitchlfo[2]; FDCT = pitchlfo[3]
	print 'delay=%d frequency=%d amplitude=%d fade_time=%d' % (DLY, FRQR, HT, FDCT)
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printlayer(layer, layer_id):
	print '------------------------------------------------------------------------------------------'
	print 'Layer %d' % (layer_id)
	start_note = layer[0x0]; end_note = layer[0x1]
	PEON = layer[0x2] >> 7    # Software PEG on
	PLON = (layer[0x2] >> 6) & 0x1    # Software PLFO on
	FMCB = (layer[0x2] >> 5) & 0x1    # FM carrier
	SBCTL = (layer[0x2] >> 1) & 0x3    # Source bit control
	SSCTL = ((layer[0x2] & 0x1) << 1) | (layer[0x3] >> 7)    # Source sound control
	LPCTL = (layer[0x3] >> 5) & 0x3    # Loop control
	PCM8B = (layer[0x3] >> 4) & 0x1    # 8-bit PCM
	SA = ((layer[0x3] & 0xF) << 16) | unpack('>H', layer[0x4:0x6])[0]    # Start address
	LSA = unpack('>H', layer[0x6:0x8])[0]    # Loop start address
	LEA = unpack('>H', layer[0x8:0xA])[0]    # Loop end address
	D2R = layer[0xA] >> 3    # Decay 2 rate
	D1R = ((layer[0xA] & 0x7) << 2) | (layer[0xB] >> 6)    # Decay 1 rate
	EGHOLD = (layer[0xB] >> 5) & 0x1    # EG hold
	AR = layer[0xB] & 0x1F    # Attack rate
	LPSLNK = layer[0xC] >> 6    # Loop start link
	KRS = (layer[0xC] >> 3) & 0x7    # Key rate scaling
	DL = ((layer[0xC] & 0x3) << 1) | (layer[0xD] >> 5)    # Decay level
	RR = layer[0xD] & 0x1F    # Release rate
	MWH = layer[0xE] >> 7    # Hardware LFO
	MWE = (layer[0xE] >> 6) & 0x1    # Mod wheel PEG
	MWL = (layer[0xE] >> 5) & 0x1    # Mod wheel PLFO
	STWINH = (layer[0xE] >> 1) & 0x1    # Stack write inhibit
	SDIR = layer[0xE] & 0x1    # Sound direct
	TL = layer[0xF]    # Total level
	MDL = layer[0x10] >> 4    # Modulation level
	MDXSL = ((layer[0x10] & 0xF) << 2) | (layer[0x11] >> 6)    # Modulation input X
	MDYSL = layer[0x11] & 0x3F    # Modulation input Y
	OCT = (layer[0x12] >> 3) & 0xF    # Octave
	FNS = ((layer[0x12] & 0x3) << 8) | layer[0x13]    # Frequency number switch
	LFORE = layer[0x14] >> 7    # LFO reset
	LFOF = (layer[0x14] >> 2) & 0x1F    # LFO frequency
	PLFOWS = layer[0x14] & 0x3    # LFO FM wave
	PLFOS = layer[0x15] >> 5    # LFO FM level
	ALFOWS = (layer[0x15] >> 3) & 0x3    # LFO AM wave
	ALFOS = layer[0x15] & 0x7    # LFO AM level
	ISEL = (layer[0x17] >> 3) & 0xF    # Input select
	IMXL = layer[0x17] & 0x7    # Input mix level
	DISDL = layer[0x18] >> 5    # Direct send level
	DIPAN = layer[0x18] & 0x1F    # Direct panpot
	base_note = layer[0x19]
	fine_tune = unpack('b',layer[0x1A:0x1B])[0]
	fm_gen1 = layer[0x1B] >> 7
	fm_layer1 = layer[0x1B] & 0x7F
	fm_gen2 = layer[0x1C] >> 7
	fm_layer2 = layer[0x1C] & 0x7F
	velocity_id = layer[0x1D]
	peg_id = layer[0x1E]
	plfo_id = layer[0x1F]
	print 'start_note=%d end_note=%d base_note=%d fine_tune=%d' % (start_note, end_note, base_note, fine_tune)
	print 'fm_carrier=%d software_peg=%d software_plfo=%d' % (FMCB, PEON, PLON)
	print 'hardware_lfo=%d peg_mod_wheel=%d plfo_mod_wheel=%d' % (MWH, MWE, MWL)
	print 'fm_gen1=%d fm_layer1=%d fm_gen2=%d fm_layer2=%d' % (fm_gen1, fm_layer1, fm_gen2, fm_layer2)
	print 'velocity_id=%d peg_id=%d plfo_id=%d' % (velocity_id, peg_id, plfo_id)
	print '--------------------------------------------------------'
	print 'SCSP slot register load:'
	print '--------------------------------------------------------'
	print 'SBCTL=%d SSCTL=%d LPCTL=%d PCM8B=%d    \t# Source bit/Sound source/Loop controls, 8-bit PCM mode' % (SBCTL, SSCTL, LPCTL, PCM8B)
	print 'SA=0x%05X LSA=0x%04X LEA=0x%04X    \t# Start/Loop start/Loop end addresses' % (SA, LSA, LEA)
	print 'D2R=%d D1R=%d EGHOLD=%d AR=%d       \t# Decay rates, EG hold mode, Attack rate' % (D2R, D1R, EGHOLD, AR) 
	print 'LPSLNK=%d KRS=%d DL=%d RR=%d    \t\t# Loop start link, Key rate scaling, Decay level, Release rate' % (LPSLNK, KRS, DL, RR)
	print 'STWINH=%d SDIR=%d TL=%d    \t\t# Stack write inhibit, Sound direct, Total level' % (STWINH, SDIR, TL)
	print 'MDL=%d LFORE=%d LFOF=%d    \t\t# Modulation level, LFO reset/frequency' % (MDL, LFORE, LFOF)
	print 'PLFOWS=%d PLFOS=%d ALFOWS=%d ALFOS=%d    \t# LFO FM wave/level, LFO AM wave/level' % (PLFOWS, PLFOS, ALFOWS, ALFOS)
	print 'ISEL=%d IMXL=%d DISDL=%d DIPAN=%d    \t# Input select/mix level, Direct send level/panpot' % (ISEL, IMXL, DISDL, DIPAN)
#=====================================================================================================

#=====================================================================================================
def printvoice(voice, bank_id, voice_id):
	print '=========================================================================================='
	print 'Tone Bank %d - Voice %d' % (bank_id, voice_id)
	print '------------------------------------------------------------------------------------------'
	play_mode = (voice[0] >> 4) & 0x07
	bend_range = voice[0] & 0x0F
	portamento_time = voice[1]
	nlayers = unpack('b',voice[2:3])[0] + 1
	volume_bias = unpack('b',voice[3:4])[0]
	print '%d layer(s)' % nlayers
	print 'play_mode=%d bend_range=%d portamento_time=%d volume_bias=%d' % (play_mode, bend_range, portamento_time, volume_bias)
	for layer_id in range(0,nlayers):
		layer = getlayer(voice, layer_id)
		printlayer(layer, layer_id)
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printtonebank(tonebank, bank_id, voice_list=None):
	mixer_offset = unpack('>H', tonebank[0x0:0x2])[0]
	velocity_offset = unpack('>H', tonebank[0x2:0x4])[0]
	peg_offset = unpack('>H', tonebank[0x4:0x6])[0]
	plfo_offset = unpack('>H', tonebank[0x6:0x8])[0]
	voice_offset = unpack('>H', tonebank[0x8:0xA])[0]
	nmixers = (velocity_offset - mixer_offset) / 0x12
	nvelocities = (peg_offset - velocity_offset) / 0xA
	npegs = (plfo_offset - peg_offset) / 0xA
	nplfos = (voice_offset - plfo_offset) / 0x4
	nvoices = (mixer_offset - 8) / 2
	if voice_list==None or voice_list==[None]:
		voice_list = range(0,nvoices)
	for mixer_id in range(0,nmixers):
		mixer = getmixer(tonebank, mixer_id)
		printmixer(mixer, bank_id, mixer_id)
	for velocity_id in range(0,nvelocities):
		velocity = getvelocity(tonebank, velocity_id)
		printvelocity(velocity, bank_id, velocity_id)
	for peg_id in range(0,npegs):
		pitchenvelope = getpitchenvelope(tonebank, peg_id)
		printpitchenvelope(pitchenvelope, bank_id, peg_id)
	for plfo_id in range(0,nplfos):
		pitchlfo = getpitchlfo(tonebank, plfo_id)
		printpitchlfo(pitchlfo, bank_id, plfo_id)
	for voice_id in voice_list:
		voice = getvoice(tonebank, voice_id)
		printvoice(voice, bank_id, voice_id)
#=====================================================================================================

#=====================================================================================================
def printtrackblock(trackblock, bank_id, track_id, flags):
	print '=========================================================================================='
	print 'Sequence Bank %d - Track %d' % (bank_id, track_id)
	print '------------------------------------------------------------------------------------------'
	resolution = unpack('>H', trackblock[0x0:0x2])[0]
	ntempos = unpack('>H', trackblock[0x2:0x4])[0]
	data_offset = unpack('>H',trackblock[0x4:0x6])[0]
	loop_offset = unpack('>H',trackblock[0x6:0x8])[0]
	loop_point = (loop_offset - 0x8)/8
	tempo_data = unpack('>'+'I'*2*ntempos,trackblock[0x8:0x8+8*ntempos])
	steps_list = tempo_data[::2]
	tempo_list = tempo_data[1::2]
	print 'Resolution : %d steps/quarter-note' % resolution
	for tempo_event in range(0,ntempos):
		steps = steps_list[tempo_event]
		tempo = tempo_list[tempo_event]
		if tempo_event == loop_point and loop_point > 0:
			end_str = '<---- Loop point'
		else:
			end_str = ''
		print 'Tempo Event %2d: %7d steps, %7d microseconds/quater-note %s' % (tempo_event, steps, tempo, end_str)
	print '------------------------------------------------------------------------------------------'
	trackdata = gettrackdata(trackblock)
	if flags['s']:
		(bank_list, voice_list) = printtrackdata(trackdata)
	else:
		(bank_list, voice_list) = printtrackvoices(trackdata)
	print '=========================================================================================='
	print '\n'
	return (bank_list, voice_list)
#=====================================================================================================

#=====================================================================================================
def printsequencebank(sequencebank, bank_id, flags):
	ntracks = unpack('>H', sequencebank[0x0:0x2])[0]
	for track_id in range(0,ntracks):
		trackblock = gettrackblock(sequencebank, track_id)
		printtrackblock(trackblock, bank_id, track_id, flags)
#=====================================================================================================

#=====================================================================================================
def printdspbank(dspbank, bank_id):
	name = dspbank[0x0:0x20].tostring().replace('\x00',' ').strip()
	print '=========================================================================================='
	print 'DSP Program Bank %d - % s' % (bank_id, name)
	print '------------------------------------------------------------------------------------------'
	rbl = 1 << (dspbank[0x20] + 13)
	coef = map(lambda x: x >> 3, unpack('>'+'h'*64,dspbank[0x40:0xC0]))
	madrs = unpack('>'+'H'*64,dspbank[0xC0:0x140])
	if len(dspbank) < 0x540:
		mpro_data = unpack('>'+'Q'*128,dspbank[0x140:])
	else:
		mpro_data = unpack('>'+'Q'*128,dspbank[0x140:0x540])
	last = len(mpro_data)
	found_last = 0
	max_cra = 0
	max_masa = 0
	for idx in range(len(mpro_data)-1,0,-1):
		if mpro_data[idx] != 0 and not found_last:
			last = idx
			found_last = 1
		max_cra = max(max_cra, mpro(mpro_data[idx]).CRA)
		max_masa = max(max_masa, mpro(mpro_data[idx]).MASA)
	mpro_data = mpro_data[:last+1]
	coef = coef[:max_cra+1]
	madrs = madrs[:max_masa+1]
	print '# Ring-buffer length in samples'
	print 'RBL=0x%X' % rbl
	print '------------------------------------------------------------------------------------------'
	print '# DSP program coefficients'
	for idx in range(0,len(coef)):
		print ('COEF[%02d]=%.5g' % (idx, coef[idx]/4096.)).ljust(20),
		if (idx & 3) == 3 or idx == len(coef)-1:
			print ''
	print '------------------------------------------------------------------------------------------'
	print '# Ring-buffer offsets in milliseconds delayed from the current sample (rate=44100 Hz)'
	for idx in range(0,len(madrs)):
		print ('MADRS[%02d]=%.1f' % (idx, madrs[idx]*1000./44100.)).ljust(20),
		if (idx & 3) == 3 or idx == len(madrs)-1:
			print ''
	print '------------------------------------------------------------------------------------------'
	print '# DSP program instructions'
	print '#   Externals (MIXS: from input mixer, EXTS: CDDA input, RB: ring-buffer, EFREG: to output mixer)'
	print '#   Macros (SAT: saturate output, NOFL: do not convert to ring-buffer floating-point format, NOP: no operation)'
	print '#   DEC is a counter which decrements after every sample'
	print '#'
	for idx in range(0,len(mpro_data)):
		# Get current and next instruction, check for ACC occurences in next instruction
		# If not found, remove ACC assignment in current instruction
		mpro_curr = mpro(mpro_data[idx]).dasm()
		remove_acc = 0
		if idx < len(mpro_data)-1:
			mpro_next = mpro(mpro_data[idx+1]).dasm()
			acc_idx = mpro_next.replace('ACC=','XXXX').find('ACC')    # skip ACC assignments when looking
			if acc_idx < 0:
				remove_acc = 1
		else:
			# If last instruction, always remove ACC assignment
			remove_acc = 1
		if remove_acc:
			acc_start = mpro_curr.find('ACC=')
			acc_end = mpro_curr.find(';',acc_start)
			mpro_curr = mpro_curr.replace(mpro_curr[acc_start:acc_end+2],'')
		mpro_curr = mpro_curr.strip()
		# Check for NOPs
		if mpro_curr == '':
			mpro_curr = 'NOP;'
		print 'MPRO[%03d] %s' % (idx, mpro_curr)
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printdspbanksummary(ssfbin, effectbank):
	print '=========================================================================================='
	print 'DSP Bank Summary'
	print '------------------------------------------------------------------------------------------'
	for bank in range(0x0,0x10):
		(dspbank, ok) = getdspbank(ssfbin, bank)
		if ok:
			name = dspbank[0x0:0x20].tostring().replace('\x00',' ').strip()
			rbl = dspbank[0x20] & 0x3    # Ring buffer length type
			ntables = dspbank[0x21]    # Number of COEF tables
			mem_req = 0x4000*(1 << rbl) + 0xA00*ntables + 0x40
			if bank == effectbank:
				end_str = '<---- selected DSP program'
			else:
				end_str = ''
			print 'DSP Bank %2d:   %s (0x%X bytes DSP RAM required) %s' % (bank, name, mem_req, end_str)
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printtonebanksummary(ssfbin, mixerbank, mixer_id):
	print '=========================================================================================='
	print 'Tone Bank Summary'
	print '------------------------------------------------------------------------------------------'
	mixer_found = 0
	for bank in range(0x0,0x10):
		(tonebank, ok) = gettonebank(ssfbin, bank)
		if ok:
			mixer_offset = unpack('>H', tonebank[0x0:0x2])[0]
			velocity_offset = unpack('>H', tonebank[0x2:0x4])[0]
			peg_offset = unpack('>H', tonebank[0x4:0x6])[0]
			plfo_offset = unpack('>H', tonebank[0x6:0x8])[0]
			voice_offset = unpack('>H', tonebank[0x8:0xA])[0]
			nmixers = (velocity_offset - mixer_offset) / 0x12
			nvelocities = (peg_offset - velocity_offset) / 0xA
			npegs = (plfo_offset - peg_offset) / 0xA
			nplfos = (voice_offset - plfo_offset) / 0x4
			nvoices = (mixer_offset - 8) / 2
			if bank == mixerbank:
				end_str = '<---- *'
				mixer_found = 1
			else:
				end_str = ''
			print 'Tone Bank %2d: %3d mixer(s), %3d velocity(s), %3d PEG(s), %3d PLFO(s), %3d voice(s) %s' % \
			(bank, nmixers, nvelocities, npegs, nplfos, nvoices, end_str)
	if mixer_found:
		print ''
		print '* selected mixer bank (mixer %d)' % mixer_id
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printsequencebanksummary(ssfbin, seqbank, seqtrack):
	print '=========================================================================================='
	print 'Sequence Bank Summary'
	print '------------------------------------------------------------------------------------------'
	for bank in range(0x0,0x10):
		(sequencebank, ok) = getsequencebank(ssfbin, bank)
		if ok:
			ntracks = unpack('>H', sequencebank[0x0:0x2])[0]
			if bank == seqbank:
				endstr = '<---- selected sequence bank (track %d)' % seqtrack
			else:
				endstr = ''
			print 'Sequence Bank %2d: %3d track(s) %s' % (bank, ntracks, endstr)
	print '=========================================================================================='
	print '\n'
#=====================================================================================================

#=====================================================================================================
def printall(nssf,flags):
	ssfbin = ssfload(nssf)
	#fo = open('ssfbin.bin','wb')    # DEBUG
	#fo.write(ssfbin)    # DEBUG
	#fo.close()    # DEBUG
	if len(ssfbin) == 1:
		return
	printdriverversion(ssfbin)
	areamap = getareamap(ssfbin)
	printareamap(ssfbin, areamap)
	(hostcommands, seqbank, seqtrack, effectbank, mixerbank, mixer_id) = gethostcommands(ssfbin)
	printhostcommands(hostcommands)
	printsequencebanksummary(ssfbin, seqbank, seqtrack)
	printtonebanksummary(ssfbin, mixerbank, mixer_id)
	printdspbanksummary(ssfbin, effectbank)
	bank_list = set([])
	voice_list = set([])
	if flags['a']:
		for bank_id in range(0,16):
			(sequencebank, ok) = getsequencebank(ssfbin, bank_id)
			if ok:
				printsequencebank(sequencebank, bank_id, flags)
	else:
		(sequencebank, ok) = getsequencebank(ssfbin, seqbank)
		if ok:
			trackblock = gettrackblock(sequencebank, seqtrack)
			(bank_list, voice_list) = printtrackblock(trackblock, seqbank, seqtrack, flags)
	if not flags['v']:    # Only print active mixer if not in verbose mode
		(tonebank, ok) = gettonebank(ssfbin, mixerbank)
		if ok:
			mixer_offset = unpack('>H', tonebank[0x0:0x2])[0]
			velocity_offset = unpack('>H', tonebank[0x2:0x4])[0]
			nmixers = (velocity_offset - mixer_offset) / 0x12
			if mixer_id < nmixers:
				mixer = getmixer(tonebank, mixer_id)
				printmixer(mixer, mixerbank, mixer_id)    
	if flags['a']:
		bank_list = range(0,16)
	for bank in bank_list:
		(tonebank, ok) = gettonebank(ssfbin, bank)
		if ok and flags['v']:
			if flags['a']:
				printtonebank(tonebank, bank)
			else:
				voice_list[bank] = list(voice_list[bank])
				voice_list[bank].sort()
				printtonebank(tonebank, bank, voice_list[bank])
	if flags['d']:
		if flags['a']:
			for bank_id in range(0,16):
				(dspbank, ok) = getdspbank(ssfbin, bank_id)
				if ok:
					printdspbank(dspbank, bank_id)
		else:
			(dspbank, ok) = getdspbank(ssfbin, effectbank)
			if ok:
				printdspbank(dspbank, effectbank)
#=====================================================================================================

#=====================================================================================================
# ssfinfo main function
argv = sys.argv
argc = len(argv)
flags = {'a':0, 'v':0, 's':0, 'd':0}
if argc < 2:
	print 'SSF/miniSSF info generator v0.09 by kingshriek'
	print 'Usage:    python %s [option(s)] <ssf/minissf file(s)>' % os.path.basename(argv[0])
	print 'Options:'
	print '          -a    output information on all banks/tracks'
	print '          -d    output DSP program disassembly'
	print '          -s    verbose sequence data output'
	print '          -v    verbose tone bank output'
	print '          --    turn all previous flags off'
	sys.exit(0)
for arg in argv[1:]:
	if arg[0] == '-':
		for flag in arg[1:]:
			if flag in flags:
				flags[flag] = 1
			elif flag == '-':
				for flag in flags:
					flags[flag] = 0
			else:
				print 'Error: Invalid option -%s' % flag
				sys.exit()
	else:
		ssfs = glob(arg)
		for nssf in ssfs:
			printall(nssf, flags)
#=====================================================================================================

#=====================================================================================================
# 07-12-20 (v0.09) - Fixed a crash-inducing bug introduced with v0.07.
# 07-12-20 (v0.08) - Changed offset bounds on the mixer offset in the tone bank check so that the script
#     does a better job with validating tone banks. Added a bitmask to the bank select in the track data
#     routines to prevent the script from crashing occasionally.
# 07-12-18 (v0.07) - Changed tone bank output to only display voices actually used in the sequence data
#     unless -a option is also specified. Made names of the some of the layer data clearer.
# 07-11-30 (v0.06) - Added option to output DSP program disassembly. Removed OCT, FNS, MDXSL, MDYSL from
#     slot register layer data. The sound driver does not get these values from this location.
# 07-11-22 (v0.05) - Added some more modulation-related values to the layer data output.
# 07-11-07 (v0.04) - Added option to output sequence data information. Improved driver version string
#     detection.
# 07-10-27 (v0.03) - Corrected EGHOLD and MDL value outputs.
# 07-10-18 (v0.02) - Added DSP RAM requirements and validity checks on DSP RAM against these requirements.
#     Added selected mixer information to default output.
# 07-10-13 (v0.01) - Changed script to no longer print out information on all tone banks when using verbose 
#     output mode but instead only tone banks that are found to be used in the selected sequence. Added
#     another option flag, -a, to print out information on all tracks and tone banks. Added '--' flag to
#     turn all flags off. Removed dependency on psf2exe and now use Python's zlib module instead. Relaxed
#     test condition for DSP banks. Corrected loop point in the track block info. Made various output
#     formatting changes.
# 07-10-12 (v0.00) - Initial release.
#=====================================================================================================