import numpy as np
import cv2
from threading import Lock, Thread
import time
class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

    
class ImgProvider(metaclass=SingletonMeta):  
    def __init__(self, isRealsenseCamera):

        self.isRealsenseCamera = isRealsenseCamera
        self.process = Thread(target=self.__run)
        wCam, hCam = 424, 240
        fps = 6
        self.img = None
        self.sampleImagesCallback = None
        self.stopFlag = False

        if self.isRealsenseCamera :
            import pyrealsense2 as rs
            # Create a pipeline
            self.pipeline = rs.pipeline()

            # Create a config and configure the pipeline to stream
            #  different resolutions of color and depth streams
            config = rs.config()

            # Get device product line for setting a supporting resolution
            pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
            pipeline_profile = config.resolve(pipeline_wrapper)
            device = pipeline_profile.get_device()
            device_product_line = str(device.get_info(rs.camera_info.product_line))

            found_rgb = False
            for s in device.sensors:
                if s.get_info(rs.camera_info.name) == 'RGB Camera':
                    found_rgb = True
                    break
            if not found_rgb:
                print("The demo requires Depth camera with Color sensor")
                exit(0)

            config.enable_stream(rs.stream.depth, wCam, hCam, rs.format.z16, fps)
            config.enable_stream(rs.stream.color, wCam, hCam, rs.format.bgr8, fps)

            # Start streaming
            profile = self.pipeline.start(config)

            # Getting the depth sensor's depth scale (see rs-align example for explanation)
            depth_sensor = profile.get_device().first_depth_sensor()
            depth_scale = depth_sensor.get_depth_scale()
            print("Depth Scale is: " , depth_scale)

            # We will be removing the background of objects more than
            #  clipping_distance_in_meters meters away
            clipping_distance_in_meters = 1 #1 meter
            self.clipping_distance = clipping_distance_in_meters / depth_scale

            # Create an align object
            # rs.align allows us to perform alignment of depth frames to others frames
            # The "align_to" is the stream type to which we plan to align depth frames.
            align_to = rs.stream.color
            self.align = rs.align(align_to)


        
        else:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3,wCam)
            self.cap.set(4,hCam)
    def __run(self):
        start = time.time()
        while(True):
            if self.stopFlag:
                time.sleep(1)
                continue
            try:
                if self.isRealsenseCamera:
                    # Get frameset of color and depth
                    frames = self.pipeline.wait_for_frames()
                    # frames.get_depth_frame() is a 640x360 depth image

                    # Align the depth frame to color frame
                    aligned_frames = self.align.process(frames)

                    # Get aligned frames
                    aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
                    color_frame = aligned_frames.get_color_frame()

                    # Validate that both frames are valid
                    if not aligned_depth_frame or not color_frame:
                        continue

                    depth_image = np.asanyarray(aligned_depth_frame.get_data())
                    color_image = np.asanyarray(color_frame.get_data())

                    # Remove background - Set pixels further than clipping_distance to grey
                    grey_color = 153
                    depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
                    # img is background removed image
                    self.img = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

            
                else:
                    success, self.img = self.cap.read()

                sampleImagesCallback, interval = self.sampleImagesCallback
                end = time.time()
                if end - start > interval:
                    sampleImagesCallback(self.img)
                    start = end

            except: 
                import traceback
                traceback.print_exc()
                pass
            
                    
    def runWithThread(self):
        if not self.process.is_alive():
            self.process.start()
        else: 
            print("process is already alive", self.process.is_alive())

    def getImage(self):
        return self.img
    def setSampleImagesCallback(self, sampleImagesCallback, interval):
        self.sampleImagesCallback = (sampleImagesCallback, interval)
    



if __name__ == "__main__":
    # this is a test
    singleton = ImgProvider(True)
    singleton.runWithThread()

    while(True):

        try:
            # print(singleton.getImage())
            cv2.imshow("myimg" ,singleton.getImage())

        except:
            # import traceback
            # traceback.print_exc()
            pass
        cv2.waitKey(10) # almost always 10 miliseconds is good enough for showing a good image
