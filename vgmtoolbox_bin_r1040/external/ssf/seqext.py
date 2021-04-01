# =====================================================================================================
# Sega Saturn sequence data extractor(ver 0.07 2008-10-12)  by kingshriek
# Command-line interface script to extract sequence data out of a file/archive 
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
def seqext(finame, outdir):
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
	iseq = 0
	comlen = [5]*0x80 + [1,4,2,1] + [1]*0x1C + [4]*0x20 + [3]*0x30 + [1]*0x10    # sequence command length table
	try:
		while offset < fisz:
			# run through file, testing for sequence data long the way
			offset = fimap.find('\x00',offset)    # to speed things up a bit
			ntrack = unpack('>H',fimap[offset:offset+2])[0]    # number of tracks
			ftrack = unpack('>I',fimap[offset+2:offset+6])[0]    # first track offset
			if ntrack>0 and ntrack<128 and 4*ntrack+2 == ftrack:    # test 1 - check consistency of number of tracks with first track offset
				atrack = unpack('>I',fimap[offset+4*(ntrack-1)+2:offset+4*(ntrack-1)+6])[0]    # last track offset - assuming tracks are ordered sequentially
				if offset+atrack+6 < fisz:    # test 2 - check last track offset
					ntmp = unpack('>H',fimap[offset+atrack+2:offset+atrack+4])[0]
					aseq = unpack('>H',fimap[offset+atrack+4:offset+atrack+6])[0]    # first command offset of last track
					offseq = offset + atrack + aseq
					if offseq < fisz and 8*ntmp+0x8 == aseq:    # test 3 - check tempo offset consistency
						# To get the sequence data size, run through sequence data commands until end of track is reached 
						while offseq < fisz:
							com = unpack('B',fimap[offseq])[0]
							offseq += comlen[com]
							if com == 0x83:    # end of track
								break
						fname = finoext + '_%03d.SEQ' % iseq
						iseq += 1
						print '%s [0x%08X]: %d bytes, %d track(s)' % (fname,offset,offseq-offset,ntrack)
						fo = open(os.path.join(outdir,fname),'wb')
						fo.write(fimap[offset:offseq])
						fo.close()
						offset = offseq - 1    # set file offset to end of track offset
			offset += 1
	except:
		return iseq
	return iseq
# -----------------------------------------------------------------------------------------------------
	fimap.close()
	fi.close()
# =====================================================================================================

# =====================================================================================================
if __name__ == '__main__':
	argv = sys.argv
	argc = len(argv)
	if argc < 3:
		print 'Sega Saturn sequence extractor v0.07 by kingshriek'
		print 'Usage: python %s <filename(s)> <output directory>' % argv[0]
		sys.exit()
	outdir = argv[-1]
	if not os.path.exists(outdir):
		os.mkdir(outdir)
	for arg in argv[1:-1]:
		finames = glob(arg)
		for finame in finames:
			iseq = seqext(finame,outdir)
			if iseq == 0:
				print '--- %s: No sequence data found' % finame
# =====================================================================================================

# =====================================================================================================
# Update history:
# 08-10-12 (0.07) - Added __name__ == '__main__' statement. Script will now create output directory
#                   if it doesn't exist.
# 07-11-10 (0.06) - Made the script much faster.
# 07-10-30 (0.05) - Replaced newline output when no sequence data found with meaningful text. Changed script
#     so that is skips over directories instead of returning an error.
# 07-10-18 (0.04) - Added support for multiple input files.
# 07-10-12 (0.03) - Made mmap use portable again.
# 07-10-09 (0.02) - Found some sequence data that didn't start with a control change event. Changed test 3
#     to check tempo offset consistency intstead.
# 07-10-04 (0.01) - Fixed some bounding errors on the sequence offsets. Made the sequence run-through
#     table-driven. Changed mmap to ACCESS_READ.
# 07-10-03 (0.00) - initial version
# =====================================================================================================