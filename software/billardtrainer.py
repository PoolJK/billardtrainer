#!/usr/bin/python3
import argparse
import cv2

from raspy.detect_test import DetectTest
from test_ui import test_ui

clParser = argparse.ArgumentParser()
clParser.add_argument('-f', '--file', dest="filename", help="input (device, file, video, stream)",
                      required=False)
clParser.add_argument('-cf', '--calibration-file', dest="cal_filename",
                      help="input for calibration (device, file, video, stream)", required=False)
clParser.add_argument('-res', dest='res', help='display resolution', required=False)
clParser.add_argument('-pc', dest="pc_test", help="for testing on pc",
                      action="store_true", default=False)
clParser.add_argument('-ui', dest="use_ui", help="use user interface, assumes -pc",
                      action="store_true", default=False)
clParser.add_argument('-d', '--debug', dest="debug", help="show more debug output",
                      action="store_true", default=False)
clParser.add_argument('-push', '--push-to-pi', dest="push_to_pi", help="push sources to pi",
                      action="store_true", default=False)
args = clParser.parse_args()
if args.push_to_pi:
    # remove -push and -pc flags if set
    import sys
    sys.argv.remove('-push')
    if '-pc' in sys.argv:
        sys.argv.remove('-pc')
    import os
    # push to pi
    if os.name == 'nt':
        # push only modified files
        from git import Repo
        repo = Repo(os.pardir)
        for diff in repo.head.commit.diff(None):
            # push file to pi using pscp (putty)
            os.system('pscp -pw pi ../{} pi@raspberrypi:/home/pi/billardtrainer/{}'.format(diff.b_path, diff.b_path))
        # save args to pi_command file used by putty
        cmd = open('pi_command', 'w')
        args = ''
        # get string from args
        for a in sys.argv[1:]:
            args += ' ' + a
        cmd.write('export DISPLAY=:0 && cd /home/pi/billardtrainer/software && lxterminal --command="python3 '
                  '\'/home/pi/billardtrainer/software/billardtrainer.py\'' + args + '"\n')
        cmd.close()
        # run the program on the pi
        os.system('putty -ssh -2 -l pi -pw pi -m c:pi_command raspberrypi')
    # TODO: elif os.name == unix: ...
    # TODO: elif os.name == osx: ...
    # exit, you're done on PC
    exit(0)
if args.use_ui:
    args.pc_test = True
    test_ui.main(args)
    exit(0)
try:
    # if you're here, you might be on the pi, so try to catch all errors
    detect_test = DetectTest(args)
    detect_test.main()
except:
    # wait to be able to read console output on raspberry pi before closing terminal on error:
    cv2.waitKey()
    cv2.waitKey()
exit(0)
