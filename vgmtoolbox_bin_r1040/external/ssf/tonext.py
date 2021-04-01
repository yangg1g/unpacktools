# =====================================================================================================
# Sega Saturn tone data extractor(ver 0.07 2008-10-12)  by kingshriek
# Command-line interface script to extract tone data out of a file/archive 
# Update history located near end of file
# =====================================================================================================

# =====================================================================================================
import os
import sys
import mmap
from struct import *
from glob import *
# =====================================================================================================

# =====================================================================================================
def tonext(finame,outdir):
	try:
		fi    = open(finame,'rb')
	except:
		return -1
	fisz  = os.path.getsize(finame)
	fimap = mmap.mmap(fi.fileno(),fisz,access=mmap.ACCESS_READ)
# -----------------------------------------------------------------------------------------------------
	fibase = os.path.basename(finame)
	idot  = -fibase[::-1].find('.')-1
	if idot:
		finoext = fibase[:idot]
	else:
		finoext = fibase
# -----------------------------------------------------------------------------------------------------
	offset = 0x00
	ibin = 0
	samplesize = [2,1]    # sample size list for PCM8B (in bytes)
	unitdatasize = [0x12,0x0A,0x0A,0x04]    # unit data sizes in bytes for mixer,VL,PEG,PLFO data respectively
	layersize = 0x20    # unit data size for layer data
	try:
		while offset < fisz:
			offset = fimap.find('\x00',offset)    # will miss banks with between 125 and 128 different mixers, but that's highly unlikely
			offmix    = unpack('>H',fimap[offset:offset+2])[0]    # mixer offset
			if offmix >= 0x000A and offmix < 0x0108:    # test 1 - mixer offset should be consistent number of voices should be between 1 and 128
				offvl     = unpack('>H',fimap[offset+2:offset+4])[0]    # VL offset
				offpeg    = unpack('>H',fimap[offset+4:offset+6])[0]    # PEG offset
				offplfo   = unpack('>H',fimap[offset+6:offset+8])[0]    # PLFO offset				
				nvoices = (offmix - 8)/2
				offvoices = unpack('>'+'H'*nvoices,fimap[offset+8:offset+8+2*nvoices])    # Voice offsets
				offset_list = (offmix, offvl, offpeg, offplfo) + offvoices
				offtonemax = 0    # maximum tone offset
				offset_diff = map(lambda x,y:x-y,offset_list[1:],offset_list[:-1])
				monotonic_sequence = (filter(lambda x:x>0,offset_diff) == offset_diff)
				if not monotonic_sequence:    # test 2 - check for monotonic sequence
					offset += 1
					continue
				deltas_consistent = (map(lambda x,y:x%y,offset_diff,unitdatasize + [layersize]*(nvoices-1)) == [0x00,0x00,0x00,0x00] + [0x4]*(nvoices-1))
				if deltas_consistent:    # test 3 - check offset deltas against unit data sizes
					# loop through voices and layers to get maximum tone offset and size
					for offvoice in offvoices:
						nlayers  = unpack('b',fimap[offset+offvoice+2])[0] + 1
						for ilayer in range(0,nlayers):
							offtone = unpack('>I',fimap[offset+offvoice+4+layersize*ilayer+2:offset+offvoice+4+layersize*ilayer+6])[0] & 0x0007FFFF
							if offtone > offtonemax:
								offtonemax = offtone
								pcm8b = (unpack('B',fimap[offset+offvoice+4+layersize*ilayer+3])[0] >> 4) & 0x1
								tonemaxsize = samplesize[pcm8b]*unpack('>H',fimap[offset+offvoice+4+layersize*ilayer+8:offset+offvoice+4+layersize*ilayer+10])[0]
								#print 'DEBUG: offset=%08X offvoice=%04X offtonemax=%05X pcm8b=%01X tonemaxsize=%05X' % (offset,offvoice,offtonemax,pcm8b,tonemaxsize)
					fname = finoext + '_%03d.BIN' % ibin
					ibin += 1
					print '%s [0x%08X]: %d bytes, %d voice(s)' % (fname,offset,offtonemax+tonemaxsize,nvoices)
					fo = open(os.path.join(outdir,fname),'wb')
					fo.write(fimap[offset:offset+offtonemax+tonemaxsize])
					fo.close()
					offset += offtonemax+tonemaxsize-1    # set file offset to last byte of tone data
			offset += 1
	except:
		return ibin
	return ibin
# -----------------------------------------------------------------------------------------------------
	fimap.close()
	fi.close()
# =====================================================================================================

# =====================================================================================================
if __name__ == '__main__':
	argv = sys.argv
	argc = len(argv)
	if argc < 3:
		print 'Sega Saturn tone extractor v0.07 by kingshriek'
		print 'Usage: python %s <filename(s)> <output directory>' % argv[0]
		sys.exit()
	outdir = argv[-1]
	if not os.path.exists(outdir):
		os.mkdir(outdir)
	for arg in argv[1:-1]:
		finames = glob(arg)
		for finame in finames:
			ibin = tonext(finame,outdir)
			if ibin == 0:
				print '--- %s: No tone data found' % finame
# =====================================================================================================

# =====================================================================================================
# Update history:
# 08-10-12 (0.07) - Added __name__ == '__main__' statement. Script will now create output directory
#                   if it doesn't exist.
# 07-11-10 (0.06) - Made the script a bit faster.
# 07-10-30 (0.05) - Replaced newline output when no sequence data found with meaningful text. Changed script
#     so that is skips over directories instead of returning an error.
# 07-10-30 (0.04) - Null update. Just to get seqext.py and tonext.py consistent in version number.
# 07-10-18 (0.03) - Added support for multiple input files.
# 07-10-12 (0.02) - Made mmap use portable again.
# 07-10-04 (0.01) - Corrected number of layers value to be a signed quantity. Changed mmap to ACCESS_READ.
# 07-10-03 (0.00) - initial version
# =====================================================================================================