import subprocess, os, time, sys, re
import argparse

# todo: custom maya arg(s) incl. file convert (bam2maya, etc.)
# bonus: --panda_path <path/to/panda3d/bin>

# Argument Handler #
# in the future should have a few selective args:
"""
convert.py --egg2maya --mayaver 2016 -r -v
"""
parser = argparse.ArgumentParser()
parser.add_argument('--all-phases', '--all_phases', action='store_true', help='Convert all phase files folders. (3 to 14)')
parser.add_argument('--selected_phases', '--phase', action='extend', nargs='+', type=str, help='List phase files folders to convert.')
parser.add_argument('--bam2egg', '--to_egg', '--to-egg', action='store_true', help='Convert BAM file(s) into EGG file(s).')
parser.add_argument('--egg2bam', '--to_bam', '--to-bam', action='store_true', help='Convert EGG file(s) into BAM file(s).')
parser.add_argument('--egg2maya', action='store_true', help=' Convert EGG file(s) into Maya Binary files.') # prob the best thing to do later is have another arg for what version of maya
parser.add_argument('--mayaver', '--mayaversion', '-mv', action='store', nargs='?', type=str, default='2016', help='Use specific maya version.')
parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output.')
parser.add_argument('--recursive', '-r', action='store_true', help='Convert all folders in the directory, recursively.')
args = parser.parse_args()

# Config #
#mayaArgs = "-a -m"
allFiles = []

settings = None # [ inputFile, outputFile, tool ]
bam2egg = ['.bam', '.egg', 'bam2egg.exe']
egg2bam = ['.egg', '.bam', 'egg2bam.exe']
egg2maya = ['.egg', '.mb', 'egg2maya%s.exe' % args.mayaver]
# maya converter isn't portable, have to use the one panda provides...
# for now, egg is only accepted. we can allow for bams later.

if args.all_phases:
    args.selected_phases = ['3', '3.5', '4', '5', '5.5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
if args.bam2egg: # --to-egg
	settings = bam2egg
elif args.egg2bam: # --to-bam
	settings = egg2bam
elif args.egg2maya: # later on add different maya versions!
	settings = egg2maya

# make sure a conversion method was properly inputted
if settings is None:
	parser.print_help()
	sys.exit()

# aliases
inputFile, outputFile, tool = settings
verbose = args.verbose
recursive = args.recursive
selectedPhases = args.selected_phases
	
if (not recursive) and selectedPhases:
	recursive = True # we're gonna do recursion on the phases anyway
	
if verbose and selectedPhases:
	print(selectedPhases)

start = int(round(time.time() * 1000))
if recursive: # Recursion time!
	for phase in selectedPhases:
		if not os.path.exists('phase_%s' % phase):
			continue
		for root, _, files in os.walk('phase_%s' % phase):
			for file in files:
				if not file.endswith(inputFile): # Input file
					if verbose:
						print("Skipping %s" % file)
					continue
				if verbose:
					print("Adding %s" %file)
				file = os.path.join(root, file)
				allFiles.append(file)
else:
	for file in os.listdir('.'):
		if not file.endswith(inputFile):
			if verbose:
				print("Skipping %s" % file)
			continue
		if verbose:
			print("Adding in %s" % file)
		allFiles.append(file)
for file in allFiles:
	newFile = file.replace(inputFile, outputFile)
	if os.path.exists(newFile):
		if verbose:
			print('%s already exists' % newFile)
		continue
	if verbose:
		print("Converting %s..." % file)
	subprocess.call(['bin/%s' % tool, file, newFile])
print("Conversion complete. Total time elapsed: %d ms" % (int(round(time.time() * 1000)) - start))
							

	
