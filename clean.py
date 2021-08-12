"""
	HyperModelConvert / HyperMC
	clean.py
	Tool to clean up bulk converted files.

	Author: Loonatic
	Date: 9/15/20
"""
import subprocess, os, time, sys, re
import argparse

"""
 # Argument Handler #
 Example usage: clean.py --phase 9 --egg --maya
"""
parser = argparse.ArgumentParser()
parser.add_argument('--all-phases', '--all_phases', action='store_true', help='Convert all phase files folders. (3 to 14)')
parser.add_argument('--selected_phases', '--phase', action='extend', nargs='+', type=str, metavar='3 3.5 4', help='List phase files folders to convert.')

## Removal
parser.add_argument('--egg', '-e', action='store_true', help='Wipe all EGG files.')
parser.add_argument('--bam', '-b', action='store_true', help='Wipe all BAM files.')
parser.add_argument('--maya', '-mb', action='store_true', help='Wipe all Maya binary files.')
parser.add_argument('--obj', '-o', action='store_true', help='Wipe all OBJ files.')
parser.add_argument('--fbx', '-f', action='store_true', help='Wipe all FBX files.')

## Misc
parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output.')
parser.add_argument('--recursive', '-r', action='store_true', help='Convert all folders in the directory, recursively. Typically used if there are models outside of "phase" folders.')

args = parser.parse_args()

allFiles = []
if args.all_phases:
    args.selected_phases = ['3', '3.5', '4', '5', '5.5', '6', '7', '8', '9', '10', '11', '12', '13', '14']

# Tool settings
settings = [] # inputFile
if args.egg:
	settings.append('.egg')
if args.bam:
	settings.append('.bam')
if args.maya:
	settings.append('.mb')
if args.obj:
	settings.append('.obj')
if args.fbx:
	settings.append('.fbx')

inputFile = settings
verbose = args.verbose
recursive = args.recursive
selectedPhases = args.selected_phases

if (not recursive) and selectedPhases:
	recursive = True # we're gonna do recursion on the phases anyway

# Uses milliseconds for now.
start = int(round(time.time() * 1000))

# Atm it'll sweep through the phases x amount of times in which x = amount of different extensions to delete
# Ideally, should be optimized to remove all selected extensions when it reaches folders to check.

if recursive: # Recursion time!
	for input in inputFile:
		for phase in selectedPhases:
			if not os.path.exists('phase_%s' % phase):
				continue
			for root, _, files in os.walk('phase_%s' % phase):
				for file in files:
					if not file.endswith(input): # Input file
						if verbose:
							print("Skipping %s" % file)
						continue
					if verbose:
						print("Adding %s" %file)
					file = os.path.join(root, file)
					allFiles.append(file)
                # we do not want to wipe egg files in root right now
#   else:
#		for file in os.listdir('.'):
#			if not file.endswith(input):
#				if verbose:
#					print("Skipping %s" % file)
#				continue
#			if verbose:
#				print("Adding in %s" % file)
#			allFiles.append(file)
	for file in allFiles:
		if verbose:
			print("Removing %s..." % file)
		os.remove(file)
print("Conversion complete. Total time elapsed: %d ms" % (int(round(time.time() * 1000)) - start))
