from threading import Thread
import queue
from queue import Queue

from .utils import *


class InputStream:
    def __init__(self, device, height=None, width=None, queue_size=1, debug=False):
        self.debug = debug
        self.onpi = cv2.getVersionMajor() < 4
        self.device = device
        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.last_queued = self.last_read = self.last_received = self.start = now()
        self.height = height or 1080
        self.width = width or 1920
        self.d_fps = []
        self.s_fps = []
        self.n_frames = 0
        self.Q = Queue(queue_size)
        self.last = None
        self.stream = self.open(device)

    def open(self, device=None):
        if hasattr(self, 'stream') and self.stream.isOpened():
            pass
        else:
            if device is None:
                if self.device is None:
                    print('InputStream: open: error opening stream: no device specified')
                    return 0
                device = self.device
            self.stream = cv2.VideoCapture(device)
        # TODO: V4L & Stream workaround for FRAME_COUNT
        self.n_frames = self.stream.get(cv2.CAP_PROP_FRAME_COUNT)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.width = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.last_queued = self.last_read = self.last_received = self.start = now()
        self.d_fps = []
        # V4L doesn't support fps property
        if device == 0:
            self.d_fps.append(1)
        else:
            self.d_fps.append(self.stream.get(cv2.CAP_PROP_FPS))
        self.s_fps = []
        self.s_fps.append(0.0)
        self.stopped = False
        return self.stream

    def start_capture(self):
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.t.start()
        return self

    def update(self):
        while True:
            # print('\nupdate loop start')
            n = now()
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # check time since last received image
            if dt(self.last_received, n) > 20000:
                if self.debug:
                    lp('InputStream.thread: input timed out after 20s, stopping')
                self.stop_capture()
                return
            # read the next frame
            try:
                grabbed, frame = self.stream.read()
            except Exception as e:
                lp('error grabbing frame: {}'.format(e))
                grabbed, frame = None, None
            # fix single image input
            if self.n_frames == 1 and self.last is not None:
                grabbed = True
                frame = self.last
                wait(25)
            if grabbed:
                t_s_last = dt(self.last_received, n)
                self.last_received = n
                if 10 < t_s_last < 2000:
                    self.s_fps.append(1000/t_s_last)
                else:
                    self.s_fps.append(0)
                # add to output queue
                # push one out if full
                if self.Q.full():
                    try:
                        _ = self.Q.get_nowait()
                    except queue.Empty:
                        pass
                self.Q.put(frame)
                self.last_queued = n
                self.last = frame
            else:
                wait(1000)
            # print('\nupdate loop end')

    def set(self, p1, p2):
        # set flags of stream (if exists)
        if not hasattr(self, 'stream'):
            if self.debug:
                print('InputStream: set called, but stream is None')
            return 0
        ret = self.stream.set(p1, p2)
        self.height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        return ret

    def get(self, args):
        # return flags of stream
        if not hasattr(self, 'stream'):
            return 0
        return self.stream.get(args)

    def get_display_fps(self):
        if len(self.d_fps) == 10:
            self.d_fps.remove(self.d_fps[0])
        return round(np.average(self.d_fps), 1)

    def get_source_fps(self):
        if len(self.s_fps) == 10:
            self.s_fps.remove(self.s_fps[0])
        return round(np.average(self.s_fps), 1)

    def read(self):
        n = now()
        # print('\nread start')
        # check if still running TODO: needed?
        if self.stopped:
            if self.debug:
                lp('InputStream: failed read: source is stopped')
            return None

        # check source is still sending frames
        if dt(self.last_received, n) > 20000:
            if self.debug:
                lp('InputStream: source timed out during read() (20s), stopping')
            self.stop_capture()
            return None

        # get frame from Queue, None if timeout
        try:
            # print('getting from queue')
            frame = np.copy(self.Q.get(timeout=20))
        except queue.Empty:
            frame = None
        if frame is None:
            print('InputStream: timeout in read, device={}'.format(self.device))
            return None

        # update fps data
        d_fps = self.get_display_fps()
        s_fps = self.get_source_fps()
        t_s_read = dt(self.last_read, n)
        if t_s_read > 50/3:
            self.d_fps.append(1000 / t_s_read)
        else:
            self.d_fps.append(0)
        self.last_read = n

        # put queue- and timestamp on it
        cv2.putText(frame,
                    'q:{} tsl:{: 4d}ms fps:{: 3.1f}(display) {: 3.1f}(source)'
                    .format(self.Q.qsize(), t_s_read, d_fps, s_fps),
                    # 'some text',
                    (0, frame.shape[0]), cv2.FONT_HERSHEY_COMPLEX, max(.5, frame.shape[0] / 800),
                    (255, 255, 255), 2, cv2.LINE_AA)
        # print('\nread end')
        return frame

    def stop_capture(self):
        self.stopped = True
        if self.t.is_alive():
            self.t.join()
        try:
            self.stream.release()
        except Exception as e:
            print(e)
