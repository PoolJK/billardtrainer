import cv2
import numpy as np


class TableSim:

    def __init__(self):
        self.table_src = cv2.imread('resources/experimental/table.jpg')
        self.width = self.table_src.shape[1]
        self.height = self.table_src.shape[0]
        self.table = np.copy(self.table_src)
        cv2.namedWindow('table_sim', cv2.WINDOW_NORMAL)
        self.pos = (0, 0)
        self.b_size = (40, 40)
        cv2.setMouseCallback('table_sim', self.mouse_callback, self.b_size)
        self.old_pos = self.pos
        self.ball = cv2.resize(cv2.imread('resources/experimental/balls/red.png', cv2.IMREAD_UNCHANGED),
                               self.b_size, cv2.INTER_CUBIC)

    def start(self):
        while True:
            cv2.imshow('table_sim', self.table)
            key = cv2.waitKey(40) & 0xFF
            if key == ord('q') or key == 27:
                break
        cv2.destroyAllWindows()

    def update_table(self):
        n = 0
        for rows in self.ball:
            n += 1
            m = 0
            for pix in rows:
                o_x = m + self.old_pos[1]
                o_y = n + self.old_pos[0]
                x = m + self.pos[1]
                y = n + self.pos[0]
                if o_x < self.width and o_y < self.height:
                    self.table[o_y, o_x, :] = self.table_src[o_y, o_x, :]
                if x < self.width and y < self.height:
                    self.table[y, x, :] = self.table[y, x, :] * (1 - pix[3] // 255) + pix[:3] * (pix[3] // 255)
                m += 1

    def mouse_callback(self, event, x, y, flags, param):
        # print('flags: {} param: {}'.format(flags, param))
        if event == cv2.EVENT_LBUTTONDOWN:
            # place/drag ball
            self.old_pos = self.pos
            self.pos = (y - self.b_size[0] // 2, x - self.b_size[1] // 2)
            self.update_table()
            print('new pos = {}'.format(self.pos))
        elif event == cv2.EVENT_RBUTTONUP:
            print("x:{} y:{}".format(x, y))
