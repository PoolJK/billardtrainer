import serial
import _thread
import time
from software.raspy.visual_items.visual_item import VisualItem
from software.raspy.visual_items.ball import Ball
from software.raspy.visual_items.rectangle import Rectangle
from software.raspy.visual_items.cross import Cross

class  Laser:
    """
    Support for laser module.
    Send commands via serial port.
    Receive messages from laser module.
    (no error handling yet)
    """
# max optical angle per datasheet: 30 deg
    #portstring = '/dev/tty.usbserial-A106PZ66'
    portstring = '/dev/ttyUSB0'
    def __init__(self):

        #: distance of laser from surface to draw on
        self.dist_surface = 1580
        #: resolution of laser module
        self.steps_per_mm_x = 1.754
        self.steps_per_mm_y = 1.475
        self.steps_per_mm_size = 6.6
        #: x offset of laser from table mid point in mm
        self.offset_x = 0.0
        #: y offset of laser from table mid point in mm
        self.offset_y = 0.0
        self.object = None
        self.ser = None
        self.lastmsg = ''
        try:
            self.ser = serial.Serial(self.portstring, 9600, timeout=None)
            if not self.ser.isOpen():
                self.ser.open()
            _thread.start_new_thread(self.receive, ())
        except serial.SerialException:
            self.ser = None
            print("Konnte Com-Port nicht oeffnen!")
            return


    def receive(self):
        """
        Receive messages from laser module an print them on terminal.
        """
        msg = ''
        if self.ser.isOpen:
            while True:
                while True:
                    rec = self.ser.read()
                    if rec == b'\n':
                        break
                    try:
                        msg += rec.decode()
                    except:
                        msg += '?'
                msg.rstrip("\n\r")
                print("Received: {}\r\n".format(msg))
                self.lastmsg = msg
                msg = ''
                #time.sleep(0.1)

    def reset(self):
        """
        Reset laser module (Arduino) by opening and closing
        the serial port.
        """
        if self.ser.isOpen:
            self.ser.close()
            time.sleep(1)
            self.ser.open()

    def show_object(self, obj):
        """
        Show visual item via laser module.
        Only certain items and only one item at a time
        are supported.
        """
        self.object = obj

        if isinstance(obj, Ball):
            typename = "circ"
            xpos = obj.x
            xpos = int((obj.x - self.offset_x) * self.steps_per_mm_x)
            ypos = int((obj.y - self.offset_y) * self.steps_per_mm_y)
            size = int(obj.radius / self.steps_per_mm_size)
        elif isinstance(obj, Rectangle):
             typename = "rect"
             xpos = int((obj.x - self.offset_x) * self.steps_per_mm_x)
             ypos = int((obj.y - self.offset_y) * self.steps_per_mm_y)
             size = int(obj.length / self.steps_per_mm_size)
        elif isinstance(obj, Cross):
             typename = "cross"
             xpos = int((obj.x - self.offset_x) * self.steps_per_mm_x)
             ypos = int((obj.y - self.offset_y) * self.steps_per_mm_y)
             size = int(obj.length / self.steps_per_mm_size)
        else:
             typename = ""

        if typename != "":
            sendstr =  typename + ';' + str(xpos) + ';' + str(ypos) + ';' + str(size) + '\r'
            if self.ser != None:
                self.ser.write(sendstr.encode())
                print("Send: {}".format(sendstr))


    def clear(self):
        """
        Clear item.
        Not used yet, maybe delete later.
        """
        item = None
        sendstr = "circle" + ';' + '0' + ';' + '0' + ';' + '0' + '\r'
        if(self.ser != None):
            self.ser.write(sendstr.encode())






