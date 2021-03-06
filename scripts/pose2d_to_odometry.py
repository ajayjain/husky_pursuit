#!/usr/bin/env python
'''
Ajay Jain
July 30, 2014
ARSENL Lab, Naval Postgraduate School
'''

import roslib; roslib.load_manifest('husky_pursuit')
import rospy, math
from tf.transformations import quaternion_from_euler
from std_msgs.msg import Header
from geometry_msgs.msg import Pose2D
from nav_msgs.msg import Odometry

odom_pub = None
head = None
odom = None

def on_pose(pose):
	global odom, head
	head.stamp = rospy.Time.now()

	odom.header = head

	odom.pose.pose.position.x = pose.x
	odom.pose.pose.position.y = pose.y
	
	z = math.sin(pose.theta / 2)
	w = math.cos(pose.theta / 2)
	# Normalize quaternion
	mag = math.hypot(z, w)
	odom.pose.pose.orientation.z = z / mag
	odom.pose.pose.orientation.w = w / mag

	# quat = quaternion_from_euler(.001, .001, theta)
	# odom.pose.pose.orientation.x = quat[0]
	# odom.pose.pose.orientation.y = quat[1]
	# odom.pose.pose.orientation.z = quat[2]
	# odom.pose.pose.orientation.w = quat[3]

	odom_pub.publish(odom)

# def convert

#   u0 = sqrt(cos(e2*PI/180)*cos(e1*PI/180)+cos(e2*PI/180)*cos(e3*PI/180)-sin(e2*PI/180)*sin(e1*PI/180)*sin(e3*PI/180)+cos(e1*PI/180)* cos(e3*PI/180)+1)/2;
#   u1 = (cos(e1*PI/180)*sin(e3*PI/180)+cos(e2*PI/180)*sin(e3*PI/180)+sin(e2*PI/180)*sin(e1*PI/180)*cos(e3*PI/180))/sqrt(cos(e2*PI/180)* cos(e1*PI/180)+cos(e2*PI/180)*cos(e3*PI/180)-sin(e2*PI/180)*sin(e1*PI/180)*sin(e3*PI/180)+cos(e1*PI/180)*cos(e3*PI/180)+1)/2;
#   u2 = (sin(e2*PI/180)*sin(e3*PI/180)-cos(e2*PI/180)*sin(e1*PI/180)*cos(e3*PI/180)-sin(e1*PI/180))/sqrt(cos(e2*PI/180)*cos(e1*PI/180)+ cos(e2*PI/180)*cos(e3*PI/180)-sin(e2*PI/180)*sin(e1*PI/180)*sin(e3*PI/180)+cos(e1*PI/180)*cos(e3*PI/180)+1)/2;
#   u3 = (sin(e2*PI/180)*cos(e1*PI/180)+sin(e2*PI/180)*cos(e3*PI/180)+cos(e2*PI/180)*sin(e1*PI/180)*sin(e3*PI/180))/sqrt(cos(e2*PI/180)* cos(e1*PI/180)+cos(e2*PI/180)*cos(e3*PI/180)-sin(e2*PI/180)*sin(e1*PI/180)*sin(e3*PI/180)+cos(e1*PI/180)*cos(e3*PI/180)+1)/2;


def main():
	rospy.init_node("pose2d_to_odometry")

	own_num = rospy.get_param('~own_num', 0)
	
	global odom, head
	head = Header()
	head.stamp = rospy.Time.now()
	head.frame_id = "robot_{}/odom_combined".format(own_num)

	odom = Odometry()
	odom.child_frame_id = "robot_{}/base_footprint".format(own_num)
	o = 10**-9 # zero
	odom.pose.covariance = [1, 0, 0, 0, 0, 0,
							0, 1, 0, 0, 0, 0,
							0, 0, o, 0, 0, 0, # z doesn't change
							0, 0, 0, o, 0, 0, # constant roll
							0, 0, 0, 0, o, 0, # constant pitch
							0, 0, 0, 0, 0, o] # guess - .3 radians rotation cov
	odom.twist.covariance = [100, 0, 0, 0, 0, 0,
							 0, 100, 0, 0, 0, 0,
							 0, 0, 100, 0, 0, 0, # large covariances - no data
							 0, 0, 0, 100, 0, 0,
							 0, 0, 0, 0, 100, 0,
							 0, 0, 0, 0, 0, 100]



	global odom_pub
	odom_topic = rospy.get_param('~odometry_publish_topic', 'vo')
	pose2D_topic = rospy.get_param('~pose2D_topic', 'pose2D')
	odom_pub = rospy.Publisher(odom_topic, Odometry)
	rospy.Subscriber(pose2D_topic, Pose2D, on_pose)

	rospy.spin()

if __name__ == "__main__":
	main()