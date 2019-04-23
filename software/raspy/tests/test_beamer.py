import cv2
import argparse
from software.raspy.settings import Settings
from software.raspy.beamer import Beamer
from software.raspy.visual_items.cross import Cross
from software.raspy.visual_items.text import Text
from software.raspy.visual_items.rectangle import Rectangle


def main():
    clParser = argparse.ArgumentParser()
    clParser.add_argument('-p', '--raspy', dest="on_raspy", help="if running on raspy",
                          action="store_true", default=False)


    args = clParser.parse_args()
    if args.on_raspy:
        Settings.on_raspy = True

    # create Beamer
    myBeam = Beamer()

    myBeam.add_object(Cross(-340, -180, 50))
    myBeam.add_object(Text(-340, -180, '0'))

    myBeam.add_object(Cross(340, -180, 50))
    myBeam.add_object(Text(340, -180, '1'))

    myBeam.add_object(Cross(340 , 180, 50))
    myBeam.add_object(Text(340, 180, '2'))

    myBeam.add_object(Cross(-340, 180, 50))
    myBeam.add_object(Text(-340, 180, '3'))

    myBeam.add_object(Rectangle(-100, -100, 180))

    myBeam.show_objects()
    
    cv2.waitKey()
    myBeam.close_window()
    return 0

if __name__ == '__main__':
    main()
