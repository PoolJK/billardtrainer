#!/usr/bin/python3

import argparse

from raspy import raspy
from test_ui import test_ui

clParser = argparse.ArgumentParser()
clParser.add_argument('-f', '--file', dest="filename", help="image file to process",
                      required=False)
clParser.add_argument('-d', '--debug', dest="debug", help="show more debug output",
                      action="store_true", default=False)
clParser.add_argument('-pc', dest="pc_test", help="for testing on pc",
                      action="store_true", default=False)
clParser.add_argument('-ui', dest="use_ui", help="use user interface, assumes -pc",
                      action="store_true", default=False)
args = clParser.parse_args()

if __name__ == '__main__':
    if args.use_ui:
        args.pc_test = True
        test_ui.main(args)
    else:
        raspy.main(args)
