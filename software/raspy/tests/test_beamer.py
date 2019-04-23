from software.raspy.beamer import Beamer
from software.raspy.visual_items.cross import Cross
from software.raspy.visual_items.text import Text
from software.raspy.visual_items.rectangle import Rectangle


def main():
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

if __name__ == '__main__':
    main()