# HyperModelConvert / HyperMC v1.2.0
This tool is used to bulk convert Panda3D models to a different file format.

Currently this script supports:
* bam2egg
* egg2bam
* egg2maya
* egg2maya_legacy
* maya2egg
* maya2egg_legacy
* egg2obj
* obj2egg

By default, the Maya version is set to 2016.
With the release of v1.2.0., the script will initially run for a Maya server instead of launching a new instance per model. This speeds up conversion time significantly.
You can run any of the ``_legacy`` commands if you are having issues with the Maya server.

# Dependencies
- Python 3.8+
- argparse Python package.
- psutil Python package.
- Installation of Panda3D with Maya support (optional, only required for maya conversions.)

# Instructions
By default, the program will search for a ``bin`` folder within the same directory. To ensure that the script is pointing to the correct ``bin`` folder, you can either:
 - Replace the first line for the correct directory in ``PANDA_BIN_PATH`` file, adding the argument ``--fromfile``
 - Set the filepath by adding --bindir <FILEPATH HERE> as an argument.

If you decide to run the batch scripts, please make sure to edit the ``PPYTHON_PATH`` file to point to the correct Panda Python executable location.

For a list of commands, run either
``python convert.py --help``, or ``python convert.py --pargs`` for egg2bam/bam2egg arguments.

Example usage:
``python convert.py --bam2egg --phase 5 5.5 6``
Will convert any bam files into egg files located within phase 5, 5.5, and 6.

``python convert.py --egg2maya --mayaver 2019 --all-phases --fromfile``
Will start a maya2egg2019 conversion server, and convert any egg files to maya binaries from all the phases. It will look for the Panda3D binaries from the directory located in the ``PANDA_BIN_PATH`` file.

# Legacy Conversion
With the release of v.1.2.0., legacy BAM conversions have been deprecated. However, if you would still like to download the binaries of older Panda versions, check the releases tab.
