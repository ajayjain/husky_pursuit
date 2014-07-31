#!/usr/bin/env python
'''
Ajay Jain
July 10, 2014
ARSENL Lab, Naval Postgraduate School
'''

import roslib; roslib.load_manifest('husky_pursuit')
import rospy, math
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from husky_pursuit.msg import RelativePosition

from utils import rtheta_to_xy

STOP_THRESHOLD = 1
HALF_ROBOT_WIDTH = .7 / 2 # meters, actually, it's 670 / 2 mm
emergency = True # Emergency until first scan
got_first_scan = False
vel_pub = None

turn = Twist()
turn.angular.z = 0.3

stop = Twist()

last_vel = None
last_vel_time = None

def on_scan(scan):
	global emergency, got_first_scan

	got_first_scan = True
	theta = scan.angle_min
	angles = [scan.angle_min + i * scan.angle_increment for i in range(len(scan.ranges))]
	emergency = False
	for polar in zip(scan.ranges, angles):
		if math.radians(-30) < polar[1] < math.radians(30):
			x, y = rtheta_to_xy(polar)
			if abs(y) <= HALF_ROBOT_WIDTH and x <= STOP_THRESHOLD:
				# rospy.loginfo("Emergency: (%f m, %f deg), (%f m, %f m)", polar[0], math.degrees(polar[1]), x, y)
				emergency = True

# Only relay velocities when there isn't an emergency
def on_vel(vel):
	global last_vel, last_vel_time
	rospy.loginfo("Got vel: %f, %f", vel.linear.x, vel.angular.z)
	last_vel = vel
	last_vel_time = rospy.Time.now()
	# rospy.loginfo("Got vel: (%f, %f), emergency status: %s", vel.linear.x, vel.angular.z, str(emergency))

def main():
	global vel_pub

	rospy.init_node("seek")

	behavior_cmd_topic = rospy.get_param('~behavior_cmd_topic', 'behavior_vel')
	robot_cmd_topic = rospy.get_param('~robot_cmd_topic', 'husky/cmd_vel')
	obstacle_topic = rospy.get_param('~obstacle_topic', 'status/obstacle')
	scan_topic = rospy.get_param('~scan_topic', 'scan')

	VEL_TIMEOUT = rospy.get_param('~velocity_timeout', 1)
	
	vel_pub = rospy.Publisher(robot_cmd_topic, Twist) # global
	obstacle_pub = rospy.Publisher(obstacle_topic, Bool)
	rospy.Subscriber(behavior_cmd_topic, Twist, on_vel)
	rospy.Subscriber(scan_topic, LaserScan, on_scan)

	rate = rospy.Rate(40.0)
	while not rospy.is_shutdown():

		obstacle_pub.publish(Bool(emergency))

		# if emergency and got scan data, turn
		if got_first_scan:
			if emergency:
				vel_pub.publish(turn)
			# move for (default) 1 sec at last behavior velocity
			elif last_vel_time == None or now - last_vel_time < VEL_TIMEOUT:
				vel_pub.publish(last_vel)
			else:
				rospy.logwarn("Velocity command timeout, publishing stop message")
				vel_pub.publish(stop)
		else:
			# stop until initial scan data is recieved
			vel_pub.publish(stop)

		rate.sleep()


if __name__ == "__main__":
	main()