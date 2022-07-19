"""
    HyperModelConvert / HyperMC
    convert.py
    Tool to bulk convert Maya Binary and/or Panda3D egg/bam files.
    Offers legacy support for bulk conversion of older bam file versions.

    Author: Loonatic
    Date: 6/26/20
"""
import subprocess
import os
import time
import sys
import psutil
import argparse

# todo:
#   custom maya arg(s) incl. file convert (bam2maya, etc.)
#   support for panda args, i.e. with bam2egg -h
#   warn the user if the maya2egg_server / client is missing so we dont run into an infinite loop

"""
 # Argument Handler #
 Example usage: convert.py --egg2maya --mayaver 2016 -r -v
"""
parser = argparse.ArgumentParser()

parser.add_argument(
    '--all-phases',
    '--all_phases',
    action = 'store_true',
    help = 'Convert all phase files folders. (3 to 14)'
)
parser.add_argument(
    '--selected_phases',
    '--phase',
    action = 'extend',
    nargs = '+',
    type = str,
    metavar = '3 3.5 4',
    help = 'List phase files folders to convert.'
)
parser.add_argument(
    '--selected_folders',
    '--folder',
    '--folders',
    action = 'extend',
    nargs = '+',
    type = str,
    metavar = 'models/',
    help = 'List of folders with subfolders to convert.'
)

parser.add_argument(
    '--bindir',
    '-bin',
    '-b',
    action = 'store',
    type = str,
    help = 'Set folder path to desired Panda3D bin location',
    default = "bin/"
)
parser.add_argument(
    '--fromfile',
    '--file',
    '-f',
    action = 'store_true',
    help = 'Use this flag to read the path from the PANDA_BIN_PATH folder.'
)

## Bam
parser.add_argument(
    '--bam2egg',
    '--to_egg',
    '--to-egg',
    action = 'store_true',
    help = 'Convert BAM file(s) into EGG file(s).'
)
parser.add_argument(
    '--egg2bam',
    '--to_bam',
    '--to-bam',
    action = 'store_true',
    help = 'Convert EGG file(s) into BAM file(s).'
)

## Maya
parser.add_argument(
    '--egg2maya',
    action = 'store_true',
    help = 'Convert EGG file(s) into Maya Binary files.'
)
parser.add_argument(
    '--egg2maya_legacy',
    action = 'store_true',
    help = 'Convert EGG file(s) into Maya Binary files. [LEGACY]'
)

parser.add_argument(
    '--maya2egg',
    action = 'store_true',
    help = 'Convert Maya Binary file(s) into EGG files.'
)
parser.add_argument(
    '--maya2egg_legacy',
    action = 'store_true',
    help = 'Convert Maya Binary files into EGG file(s). [LEGACY]'
)
parser.add_argument(
    '--mayaver',
    '--mayaversion',
    '-mv',
    action = 'store',
    nargs = '?',
    type = str,
    default = '2016',
    metavar = 'MayaVersion',
    help = 'Use specific maya version. (Default is 2016)'
)

## Obj
parser.add_argument(
    '--obj2egg',
    action = 'store_true',
    help = 'Convert OBJ files into EGG files.'
)
parser.add_argument(
    '--egg2obj',
    action = 'store_true',
    help = 'Convert EGG files into OBJ files.'
)

## Fbx
parser.add_argument(
    '--fbx2egg',
    action = 'store_true',
    help = 'Convert FBX files into EGG files.'
)
parser.add_argument(
    '--egg2fbx',
    action = 'store_true',
    help = 'Convert EGG files into FBX files.'
)

## Misc
parser.add_argument(
    '--verbose',
    '-v',
    action = 'store_true',
    help = 'Enable verbose output.'
)
parser.add_argument(
    '--overwrite',
    '-o',
    action = 'store_true',
    help = 'Overwrite preexisting files.'
)
parser.add_argument(
    '--recursive',
    '-r',
    action = 'store_true',
    help = 'Convert all folders in the directory, recursively.'
           ' Typically used if there are models outside of "phase" folders.'
)

# Deprecating this feature. Go get your own Panda!
# parser.add_argument('--legacy', '--use-legacy', type=str, choices=['panda105', 'panda150', 'panda162', 'panda172',
# 'panda181'], action='store', help='Use Panda3D 1.0.5 or Panda3D 1.5.0 instead to convert LEGACY bams.')
# parser.add_argument('--panda_args', '--pargs', action='extend', nargs='+', type=str, help='Optional Panda3D args to
# pass. To get a full list, run `convert.py --pargs help`.')
# Note: Removing pargs cause I dunno how to make this pretty at the moment

args = parser.parse_args()

### End of argparse configuring ###

# If the user gave us particular folders, let's not consider them to be phase files.
selectedFolders = args.selected_folders

# Config #
# mayaArgs = "-a -m" ?
allFiles = []

if not selectedFolders:
    if args.all_phases:
        args.selected_phases = ['3', '3.5', '4', '5', '5.5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
else:
    args.selected_phases = None
    args.all_phases = None

# Tool settings
settings = None  # [ inputFile, outputFile, tool ]

## Bam
bam2egg = ['.bam', '.egg', 'bam2egg.exe']
egg2bam = ['.egg', '.bam', 'egg2bam.exe']

## Maya
egg2maya_legacy = ['.egg', '.mb', 'egg2maya%s.exe' % args.mayaver]
egg2maya = ['.egg', '.mb', 'egg2maya_client.exe']
maya2egg_legacy = ['.mb', '.egg', 'maya2egg%s.exe' % args.mayaver]
maya2egg = ['.mb', '.egg', 'maya2egg_client.exe']

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
elif args.egg2maya_legacy:
    settings = egg2maya_legacy
elif args.egg2maya:
    settings = egg2maya
elif args.maya2egg_legacy:
    settings = maya2egg_legacy
elif args.maya2egg:
    settings = maya2egg
elif args.obj2egg:  # obj->egg
    settings = obj2egg
elif args.egg2obj:  # egg->obj
    settings = egg2obj
elif args.fbx2egg:  # fbx->egg
    settings = fbx2egg
elif args.egg2fbx:  # egg->fbx
    settings = egg2obj

maya_mode = args.egg2maya or args.maya2egg
maya_legacy = args.egg2maya_legacy or args.maya2egg_legacy

# optionalArgs = []
overwriteArg = []
# if args.panda_args is not None:
#	args.panda_args = [" -" + arg for arg in args.panda_args]
# Grr this is so hacky.
#	optionalArgs = (args.panda_args)

if args.overwrite:
    overwriteArg.append('-o')

if args.fromfile:
    if not os.path.isfile("PANDA_BIN_PATH"):
        print(
            "Error: Cannot read from the PANDA_BIN_PATH file."
            " Please make sure the file exists in this directory and try again."
        )
        sys.exit()
    path = open("PANDA_BIN_PATH", 'r').readline()
    path = path.replace("\\", "/")
    defaultBin = path
else:
    defaultBin = args.bindir

# Make sure a conversion method was properly inputted
if settings is None:
    # Bug: causes the script to immaturely crash if you do not pass in any arguments
    # if args.panda_args is not None:
    #     print("#######################################################################################################")
    #     subprocess.run(['%s/%s' % (defaultBin, 'egg2bam'), '-h'])
    #     print("#######################################################################################################")
    #     subprocess.run(['%s/%s' % (defaultBin, 'bam2egg'), '-h'])
    #     print("#######################################################################################################")
    parser.print_help()
    sys.exit()

inputFile, outputFile, tool = settings
verbose = args.verbose
recursive = args.recursive
selectedPhases = args.selected_phases

if (not recursive) and (selectedPhases or selectedFolders):
    recursive = True  # we're gonna do recursion on the phases anyway

# Let's list the folders we're gonna iterate through if we wanna be verbose.
if verbose and selectedPhases:
    print(selectedPhases)
elif verbose and selectedFolders:
    print(selectedFolders)

DETACHED_PROCESS = 0x00000008  # A tad hacky, but we need this for the Maya service.
mayaProcess = tool[0:8]
mayaServer = str(mayaProcess + args.mayaver + "_bin.exe")  # maya2egg20xx_bin.exe


def checkMayaServer():
    if not mayaServer in (p.name() for p in psutil.process_iter()):
        if verbose:
            print("Attempting to start the Maya server...")
        subprocess.Popen(
            ['%s/%s%s' % (defaultBin, mayaProcess, args.mayaver), "-server"], creationflags = DETACHED_PROCESS
        )
        if verbose:
            print("Sleeping for 5 seconds...")
        time.sleep(5)  # give it some time
        checkMayaServer()
    else:
        return  # It's running, no problem.


def convertPhases(phases):
    if recursive:  # Recursion time!
        for phase in phases:
            if not os.path.exists('phase_%s' % phase):
                continue
            for root, _, files in os.walk('phase_%s' % phase):
                for file in files:
                    if not file.endswith(inputFile):  # Input file
                        if verbose:
                            print("Skipping %s" % file)
                        continue
                    if verbose:
                        print("Adding %s" % file)
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
        if os.path.exists(newFile) and not args.overwrite:
            if verbose:
                print('%s already exists' % newFile)
            continue
        if verbose:
            print("Converting %s..." % file)
        if maya_mode and not maya_legacy:
            checkMayaServer()  # Check & run for the Maya server.
        # 'bin/panda105' / 'bam2egg[.exe]' optionalArgs file.bam overwriteArg newFile.egg
        subprocess.run(['%s/%s' % (defaultBin, tool), file] + overwriteArg + [newFile])


def convertFolders(folders):
    if recursive:  # Recursion time!
        for folder in folders:
            if not os.path.exists(folder):
                continue
            for root, _, files in os.walk(folder):
                for file in files:
                    if not file.endswith(inputFile):  # Input file
                        if verbose:
                            print("Skipping %s" % file)
                        continue
                    if verbose:
                        print("Adding %s" % file)
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
        if os.path.exists(newFile) and not args.overwrite:
            if verbose:
                print('%s already exists' % newFile)
            continue
        if verbose:
            print("Converting %s..." % file)
        if maya_mode and not maya_legacy:
            checkMayaServer()  # Check & run for the Maya server.
        # 'bin/panda105' / 'bam2egg[.exe]' optionalArgs file.bam overwriteArg newFile.egg
        subprocess.run(['%s/%s' % (defaultBin, tool), file] + overwriteArg + [newFile])

# Startup #

# Uses milliseconds for now.
start = int(round(time.time() * 1000))

# Which operation are we gonna run?
if selectedPhases:
    convertPhases(selectedPhases)
elif selectedFolders:
    convertFolders(selectedFolders)
else:
    # Uhm, user should not get here. Probably a good idea to yell at 'em for invalid arguments.
    print("Error: You need to include either the selectedPhases or selectedFolders arg, but not both!")
    # Probably not a good thing to do sys.exit() since we wouldn't kill the maya process.

# Cleanup #

# One more thing, let's clean up the maya server.
if maya_mode and not maya_legacy:
    for p in psutil.process_iter():
        if p.name() is mayaServer:
            p.kill()

print("Conversion complete. Total time elapsed: %d ms" % (int(round(time.time() * 1000)) - start))
