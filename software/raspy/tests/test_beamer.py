import cv2
import argparse
from software.raspy.settings import Settings
from software.raspy.beamer import Beamer
from software.raspy.visual_items.cross import Cross
from software.raspy.visual_items.text import Text
from software.raspy.visual_items.rectangle import Rectangle


def main():
    cl_parser = argparse.ArgumentParser()
    cl_parser.add_argument('-p', '--raspy', dest="on_raspy", help="if running on raspy",
                           action="store_true", default=False)

    args = cl_parser.parse_args()
    if args.on_raspy:
        Settings.on_raspy = True

    # create Beamer
    beamer = Beamer()

    beamer.add_visual_item(Cross(-340, -180, 50))
    beamer.add_visual_item(Text(-340, -180, '0'))

    beamer.add_visual_item(Cross(340, -180, 50))
    beamer.add_visual_item(Text(340, -180, '1'))

    beamer.add_visual_item(Cross(340, 180, 50))
    beamer.add_visual_item(Text(340, 180, '2'))

    beamer.add_visual_item(Cross(-340, 180, 50))
    beamer.add_visual_item(Text(-340, 180, '3'))

    beamer.add_visual_item(Rectangle(-100, -100, 180, 90))

    beamer.show_visual_items()
    
    cv2.waitKey()
    beamer.close_window()
    return 0


main()
