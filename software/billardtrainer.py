#!/usr/bin/python3
import argparse
import os
import sys

from software.classes.utils import *
from software.raspy.detect_test import DetectTest

cl_parser = argparse.ArgumentParser()
cl_parser.add_argument('-f', '--file', dest='filename', help='input (device, file, video, stream)',
                       required=False)
cl_parser.add_argument('-c', '--calibrate', dest='calibrate', help='perform calibration', action='store_true',
                       default=False)
cl_parser.add_argument('-cf', dest='cal_filename', help='input to use in calibration', required=False)
cl_parser.add_argument('-sr', '--source-resolution', dest='sres', help='source resolution', required=False)
cl_parser.add_argument('-dr', '--display-resolution', dest='dres', help='display resolution', required=False)
cl_parser.add_argument('-pc', dest='pc_test', help='for testing on pc',
                       action='store_true', default=False)
cl_parser.add_argument('-d', '--debug', dest='debug', help='show more debug output',
                       action='store_true', default=False)
cl_parser.add_argument('-push', '--push-to-pi', dest='push_to_pi', help='push sources to pi',
                       action='store_true', default=False)
cl_parser.add_argument('-mir', '--mirror', dest='mirror', help='mirror input', action='store_true', required=False)
cl_parser.add_argument('-test', '--camera-test', dest='camera_test', help='only test specified input',
                       action='store_true', default=False)
cl_parser.add_argument('-p', '--preview', dest='preview', help='only show preview', action='store_true', default=False)
cl_parser.add_argument('-bt', dest='bt_test', help='start bluetooth test', action='store_true', default=False)
args = cl_parser.parse_args()

if args.push_to_pi:
    # remove -push and -pc flags if set
    sys.argv.remove('-push')
    if '-pc' in sys.argv:
        sys.argv.remove('-pc')
    # push to pi
    if os.name == 'nt':
        # push only modified files
        from git import Repo
        repo = Repo(os.pardir)
        for diff in repo.head.commit.diff(None):
            # push file to pi using pscp (putty)
            attempts = 0
            e = 1
            while e > 0 and attempts < 5:
                e = os.system('pscp -pw pi ../{} pi@raspberrypi:/home/pi/billardtrainer/{}'
                              .format(diff.b_path, diff.b_path))
                if e > 0:
                    print('retrying')
                if attempts == 5:
                    print('error sending to pi')
                    exit(0)
                attempts += 1
        # save args to pi_command.sh file used by putty
        cmd = open('pi_command', 'w')
        args = ''
        # get string from args
        for a in sys.argv[1:]:
            args += ' ' + a
        cmd.write('export DISPLAY=:0 && cd /home/pi/billardtrainer/software && lxterminal --command=\'python3 '
                  '"/home/pi/billardtrainer/software/billardtrainer.py"' + args + '\'\n')
        cmd.close()
        # run the program on the pi (doesn't work :'-/ )
        os.system('putty -ssh -2 -l pi -pw pi -m c:pi_command raspberrypi')
    # TODO: elif os.name == unix: ...
    # TODO: elif os.name == osx: ...
    # exit, you're done on PC
    exit(0)

print("billardtrainer.py is running")
on_pi = cv2.getVersionMajor() < 4
# on the pi try to catch all errors
try:
    if args.bt_test:
        from software.raspy import bt_test_bluez
        bt_test_bluez.run_test()
        exit(0)
    detect_test = DetectTest(args)
    if not args.camera_test and not args.preview:
        detect_test.main()
except Exception as e:
    # wait to be able to read console output on raspberry pi before closing terminal on error:
    if on_pi:
        print('\nsome error occurred: {}'.format(sys.exc_info()[0]))
        print(e.args)
        cv2.waitKey()
    raise e
exit(0)
