# convert-models
This tool is used to bulk convert Panda3D models to a different file format.
Currently this script supports:
* bam2egg
* egg2bam
* egg2maya<version> (default:2016)
* egg2obj
* obj2egg
* Legacy conversion (Panda3D 1.5.0 and Panda3D 1.0.5)


Example usage:
``python convert.py --bam2egg --phase 5 5.5 6``
Will convert any bam files into egg files located within phase 5, 5.5, and 6.

``python convert.py --bam2egg --legacy panda105 --all_phases``
Will convert any bam files using a legacy method (Panda3D 1.0.5) in all phase files within the directory.

# Dependencies 
- Python 3.8+
- argparse Python package.
- Installation of Panda3D with Maya support