@echo off

echo NOTE: Please edit the PPYTHON_PATH variable before running me!
echo Make sure that you are running on Python 3.8+

set /P PPYTHON_PATH=<PPYTHON_PATH

%PPYTHON_PATH% -m pip install -r requirements.txt
%PPYTHON_PATH% hmconvert.py --fromfile --egg2bam --all-phases
pause