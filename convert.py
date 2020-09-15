"""
	HyperModelConvert / HyperMC
	convert.py
	Tool to bulk convert Maya Binary and/or Panda3D egg/bam files.
	Offers legacy support for bulk conversion of older bam file versions.

	Author: Loonatic
	Date: 6/26/20
"""
import subprocess, os, time, sys, re
import argparse

# todo: custom maya arg(s) incl. file convert (bam2maya, etc.)
# support for panda args, i.e. with bam2egg -h
# bonus: --panda_path <path/to/panda3d/bin>

"""
 # Argument Handler #
 Example usage: convert.py --egg2maya --mayaver 2016 -r -v
"""
parser = argparse.ArgumentParser()
parser.add_argument('--all-phases', '--all_phases', action='store_true', help='Convert all phase files folders. (3 to 14)')
parser.add_argument('--selected_phases', '--phase', action='extend', nargs='+', type=str, metavar='3 3.5 4', help='List phase files folders to convert.')

## Bam
parser.add_argument('--bam2egg', '--to_egg', '--to-egg', action='store_true', help='Convert BAM file(s) into EGG file(s).')
parser.add_argument('--egg2bam', '--to_bam', '--to-bam', action='store_true', help='Convert EGG file(s) into BAM file(s).')

## Maya
parser.add_argument('--egg2maya', action='store_true', help='Convert EGG file(s) into Maya Binary files.')
parser.add_argument('--maya2egg', action='store_true', help='Convert Maya Binary files into EGG file(s).')
parser.add_argument('--mayaver', '--mayaversion', '-mv', action='store', nargs='?', type=str, default='2016', metavar='MayaVersion', help='Use specific maya version. (Default is 2016)')

## Obj
parser.add_argument('--obj2egg', action='store_true', help='Convert OBJ files into EGG files.')
parser.add_argument('--egg2obj', action='store_true', help='Convert EGG files into OBJ files.')

## Fbx
parser.add_argument('--fbx2egg', action='store_true', help='Convert FBX files into EGG files.')
parser.add_argument('--egg2fbx', action='store_true', help='Convert EGG files into FBX files.')

## Misc
parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output.')
parser.add_argument('--overwrite', '-o', action='store_true', help='Overwrite preexisting files.')
parser.add_argument('--recursive', '-r', action='store_true', help='Convert all folders in the directory, recursively. Typically used if there are models outside of "phase" folders.')
parser.add_argument('--legacy', '--use-legacy', type=str, choices=['panda105', 'panda150', 'panda162', 'panda172'], action='store', help='Use Panda3D 1.0.5 or Panda3D 1.5.0 instead to convert LEGACY bams.')
#parser.add_argument('--panda_args', '--pargs', action='extend', nargs='+', type=str, help='Optional Panda3D args to pass. To get a full list, run `convert.py --pargs help`.')
# Note: Removing pargs cause I dunno how to make this pretty at the moment

args = parser.parse_args()

# Config #
#mayaArgs = "-a -m" ?
allFiles = []
if args.all_phases:
    args.selected_phases = ['3', '3.5', '4', '5', '5.5', '6', '7', '8', '9', '10', '11', '12', '13', '14']

# Tool settings
settings = None # [ inputFile, outputFile, tool ]

## Bam
bam2egg = ['.bam', '.egg', 'bam2egg.exe']
egg2bam = ['.egg', '.bam', 'egg2bam.exe']

## Maya
egg2maya = ['.egg', '.mb', 'egg2maya%s.exe' % args.mayaver]
maya2egg = ['.mb', '.egg', 'maya2egg%s.exe' % args.mayaver]

## Obj
obj2egg = ['.obj', '.egg', 'obj2egg.exe']
egg2obj = ['.egg', '.obj', 'egg2obj.exe']

## Fbx
fbx2egg = ['.fbx', '.egg', 'fbx2egg.exe']
egg2fbx = ['.egg', '.fbx', 'egg2fbx.exe']

# for now, egg is only accepted. we can allow for bams later.

if args.bam2egg:
	settings = bam2egg
elif args.egg2bam:
	settings = egg2bam
elif args.egg2maya:
	settings = egg2maya
elif args.maya2egg:
	settings = maya2egg
elif args.obj2egg: # obj->egg
	settings = obj2egg
elif args.egg2obj: # egg->obj
	settings = egg2obj
elif args.fbx2egg: # fbx->egg
	settings = fbx2egg
elif args.egg2fbx: # egg->fbx
	settings = egg2obj

#optionalArgs = []
overwriteArg = ''
#if args.panda_args is not None:
#	args.panda_args = [" -" + arg for arg in args.panda_args]
	# Grr this is so hacky.
#	optionalArgs = (args.panda_args)
	
if args.overwrite:
	overwriteArg = '-o'
	

"""
 # Panda3D Version Bam Support [Docme]
 Panda3D 1.6.2 ~ 6.14 through 6.19
 ? RobotToon: 6.14 through 6.18 bams.

"""
legacyDir = {
	'panda105': "bin/panda105/",
	'panda150': "bin/panda150/",
	'panda162': "bin/panda162/",
	'panda172': "bin/panda172"
	}
defaultBin = "bin/" if not args.legacy else legacyDir[args.legacy]

# Make sure a conversion method was properly inputted
if settings is None:
	if args.panda_args is not None:
		print("########################################################################################################################")
		subprocess.call(['%s/%s' % (defaultBin, 'egg2bam'), '-h'])
		print("########################################################################################################################")
		subprocess.call(['%s/%s' % (defaultBin, 'bam2egg'), '-h'])
		print("########################################################################################################################")
	parser.print_help()
	sys.exit()

inputFile, outputFile, tool = settings
verbose = args.verbose
recursive = args.recursive
selectedPhases = args.selected_phases

if (not recursive) and selectedPhases:
	recursive = True # we're gonna do recursion on the phases anyway

if verbose and selectedPhases:
	print(selectedPhases)

# Uses milliseconds for now.
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
	subprocess.call(['%s/%s' % (defaultBin, tool), file] + [overwriteArg] + [newFile]) # 'bin/panda105' / 'bam2egg[.exe]' optionalArgs file.bam overwriteArg newFile.egg
	print(['%s/%s' % (defaultBin, tool), file] + [overwriteArg] + [newFile])
	#print(['%s/%s' % (defaultBin, tool), ''.join(optionalArgs), file] + [overwriteArg] + [newFile])
print("Conversion complete. Total time elapsed: %d ms" % (int(round(time.time() * 1000)) - start))
