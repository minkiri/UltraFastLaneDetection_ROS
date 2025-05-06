#!/usr/bin/env python
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultrafastLaneDetector import UltrafastLaneDetector, ModelType

class LaneDetectionNode:
    def __init__(self):
        rospy.init_node('lane_detection_node', anonymous=True)


        model_path = rospy.get_param("~model_path", "/home/minkiri/catkin_ws/src/lane_detection/src/Ultrafast_Lane_Detection_Inference_Pytorch/models/tusimple_18.pth")
        model_type = ModelType[rospy.get_param("~model_type", "TUSIMPLE")]
        use_gpu = rospy.get_param("~use_gpu", True)
        video_path = rospy.get_param("~video_path", "/home/minkiri/videos/test_video.mp4")


        self.lane_detector = UltrafastLaneDetector(model_path, model_type, use_gpu)
        self.bridge = CvBridge()


        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            rospy.logerr("can't open video: {}".format(video_path))
            exit()


        self.lane_pub = rospy.Publisher("/lane_detection/output_image", Image, queue_size=10)


        # self.image_sub = rospy.Subscriber("/usb_cam_low/image_raw", Image, self.image_callback)


    # def image_callback(self, msg):
    #     try:
    #         cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
    #         output_img = self.lane_detector.detect_lanes(cv_image)
    #         output_msg = self.bridge.cv2_to_imgmsg(output_img, "bgr8")
    #         self.lane_pub.publish(output_msg)
    #     except Exception as e:
    #         rospy.logerr(f"Error in image_callback: {e}")

    def run(self):
        rate = rospy.Rate(30)  
        while not rospy.is_shutdown() and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                rospy.loginfo("finished video")
                break
            try:
                output_img = self.lane_detector.detect_lanes(frame)
                output_msg = self.bridge.cv2_to_imgmsg(output_img, "bgr8")
                self.lane_pub.publish(output_msg)
            except Exception as e:
                rospy.logerr(f"frame processing error: {e}")
            rate.sleep()

        self.cap.release()

if __name__ == '__main__':
    try:
        lane_detection_node = LaneDetectionNode()
        lane_detection_node.run()
    except rospy.ROSInterruptException:
        pass

