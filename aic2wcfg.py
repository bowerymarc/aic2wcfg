import glob
import math
import os
import struct
import sys

"""
File translation tool to translate one TI file format to another.

Translate .cfg files from GDE to aic script files usable in
wireless configurator.	In particular the later doesn't support
the ">" continuation character.

Author:	 Marc Lindahl <marc@bowery.com
WWW:	 http://engineering.bowery.com
License: GNU General Public License
Version: 1.1 (9/3/14)

"""

def argfiles(args, onlyFiles=False):
	"""Expand arguments (globs and non-globs). Return a flat list."""
	files = []
	for arg in args:
		if ('*' in arg) or ('?' in arg):
			files.extend(glob.glob(arg))
		else:
			files.append(arg)
	if onlyFiles:
		files = filter(os.path.isfile, files)
	return files


def main(args):
	if not args:
		print 'Usage: %s <input> <output>' % sys.argv[0]
		return
		
	files = argfiles(args)
	if not files:
		print 'No matching files found.'
		return
	
	if (not os.path.exists(files[0])) or (not os.path.isfile(files[0])):
		print 'Could not find %s' % files[0] 
		return

	try:
		# We use open instead of file for backwards compability
		infile = open(files[0], 'r')
	except IOError:
		print 'Could not open %s' % files[0] 
		return

	try:
		# We use open instead of file for backwards compability
		outfile = open(files[1], 'w')
	except IOError:
		print 'Could not open %s' % files[1] 
		return
		
	waddr = 0	# last write address
	wcmd = []	# last write command
	dbytes = 0	# number of data bytes in write command 
	outcmd = '' # write command output
	
	for line in infile:
		if line[0] == "w":
			if outcmd != '':	# have a pending write need to output
				outcmd += "\n\r"
				outfile.write(outcmd)
			waddr = int( line.split()[2], 16)
			wcmd = line.split()[0:4]
			outcmd = ' '.join(wcmd)
			dbytes = 1
		elif line[0] == ">":
			#note that if waddr > 255 this will fail, but then again, the input should never have that as it couldn't autoinc that much
			if dbytes >= 254:
				outcmd += "\n\r"
				outfile.write(outcmd)
				waddr += 1
				dbytes = 1
				outcmd = ' '.join(wcmd) + (" %02x " % waddr) + line.split()[1]
			else:
				waddr += 1
				dbytes += 1
				outcmd += ' ' + line.split()[1]
		elif line[0] == "#":
			outfile.write(line)
		else:
			outcmd += "\n\r"
			outfile.write(outcmd)
			outfile.write(line)
			outcmd = ''
			wcmd = []
			dbytes = 0
	if outcmd != '':	# have a pending write need to output
		outcmd += "\n\r"
		outfile.write(outcmd)
	outfile.close()
	infile.close()

		

if __name__=='__main__':
	main(sys.argv[1:])
