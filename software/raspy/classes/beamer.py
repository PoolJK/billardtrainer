from raspy.classes import settings
from .utils import *


class Beamer:
    """
    A projector class for showing image on table.
    Needs to take offset and distance in account to correct displayed image.
    """

    def __init__(self, resolution_x=1280, resolution_y=720,
                 offset_x=0, offset_y=0,
                 ppm_x=1, ppm_y=1, rotation=270):
        """
        Define new Beamer
        :param resolution_x: image resolution in pixel
        :param resolution_y: image resolution in pixel
        :param offset_x: offset from table 0.x in mm
        :param offset_y: offset from table 0.y in mm
        :param ppm_x: pixel per mm x
        :param ppm_y: pixel per mmm y
        """
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.ppm_x = ppm_x
        self.ppm_y = ppm_y
        #: x offset of beamer from table mid point in mm
        self.offset_x = offset_x
        #: y offset of beamer from table mid point in mm
        self.offset_y = offset_y
        self.rotation = rotation

        # get Matrix
        self.matrix = cv2.getRotationMatrix2D((offset_x, offset_y), rotation, 1.0)
        #: objects to show in image
        self.objects = []
        # create black image to show objects in
        self.outPict = np.zeros((self.resolution_y, self.resolution_x, 3), np.uint8)
        print('offset(x,y)=({:.2f}, {:.2f}) ppmx={:.2f} ppmy={:.2f}'.format(self.offset_x, self.offset_y, self.ppm_x,
                                                                            self.ppm_y))
        # create window for beamer output (height, width, dimension for numpy array)
        cv2.namedWindow("beamer", cv2.WINDOW_NORMAL)
        if cv2.getVersionMajor() < 4:
            print('on raspy')
            # cv2.namedWindow('beamerdebug', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            print('on pc')

    def show_visual_items(self):
        for obj in self.objects:
            obj.draw(self.outPict, self.offset_x, self.offset_y, self.ppm_x, self.ppm_y)
        # mark middle of beamer
        if settings.debug:
            cv2.drawMarker(self.outPict, (self.outPict.shape[1] // 2,
                                          self.outPict.shape[0] // 2),
                           [0, 165, 255], cv2.MARKER_CROSS, 20, 5)
        self.show_image()

    def show_image(self, image=None):
        if image is None:
            image = self.outPict
        cv2.imshow("beamer", image)
        if not settings.on_pi:
            cv2.resizeWindow('beamer', 360, 640)

    @staticmethod
    def hide():
        cv2.destroyWindow('beamer')

    def get_image(self):
        """
        Get current outPict
        """
        return self.outPict

    def show_white(self):
        # create black image to show objects in
        white_pict = np.zeros((self.resolution_x, self.resolution_y, 3), np.uint8)
        white_pict[:] = (255, 255, 255)
        self.show_image(white_pict)

    def clear_image(self):
        self.objects.clear()
        self.outPict[:] = 0

    @staticmethod
    def close_window():
        """
        Close full size window to show raspy desktop etc.
        """
        cv2.destroyWindow("beamer")

    def add_visual_item(self, visual_item):
        """
        Add visual_item to show with show_visual_items()
        :param visual_item: some visual item
        """
        self.objects.append(visual_item)
