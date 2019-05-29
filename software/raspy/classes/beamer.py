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
        debug('beamer offset(x,y)=({:.2f}, {:.2f}) ppmx={:.2f} ppmy={:.2f}'.format(
            self.offset_x, self.offset_y, self.ppm_x, self.ppm_y))
        # create window for beamer output (height, width, dimension for numpy array)
        cv2.namedWindow("beamer", cv2.WINDOW_NORMAL)
        if cv2.getVersionMajor() < 4:
            print('on raspy')
            if not settings.debug:
                cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            print('on pc')

    @staticmethod
    def draw_objects(objects, out_pict, offset_x, offset_y, ppm_x, ppm_y):
        out_pict[:] = 0
        for obj in objects:
            obj.draw(out_pict, offset_x, offset_y, ppm_x, ppm_y)
        # mark middle of beamer
        if settings.debug:
            cv2.drawMarker(out_pict, (out_pict.shape[1] // 2,
                                      out_pict.shape[0] // 2),
                           [0, 165, 255], cv2.MARKER_CROSS, 20, 5)

    @staticmethod
    def show_image(image, rotation):
        if settings.on_pi:
            dst = rotate(image, rotation)
            cv2.imshow('beamer', dst)
        if not settings.on_pi:
            cv2.imshow("beamer", image)
            cv2.resizeWindow('beamer', 360, 640)

    def get_image(self):
        """
        Get current outPict
        """
        return self.outPict

    @staticmethod
    def hide():
        cv2.destroyWindow('beamer')

    def clear_objects(self):
        self.objects.clear()

    @staticmethod
    def close_window():
        """
        Close full size window to show raspy desktop etc.
        """
        cv2.destroyWindow("beamer")

    def add_visual_item(self, visual_item):
        """
        Add visual_item to show with draw_objects()
        :param visual_item: some visual item
        """
        self.objects.append(visual_item)
