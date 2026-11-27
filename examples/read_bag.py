#!/usr/bin/env python3
"""Read a bag without ROS running: distance driven and closest obstacle."""
import math
import sys

import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

reader = rosbag2_py.SequentialReader()
reader.open(rosbag2_py.StorageOptions(uri=sys.argv[1]),
            rosbag2_py.ConverterOptions("", ""))
reader.set_filter(rosbag2_py.StorageFilter(topics=["/odom", "/scan"]))
types = {t.name: get_message(t.type) for t in reader.get_all_topics_and_types()}

distance, last, closest, scans = 0.0, None, math.inf, 0
while reader.has_next():
    topic, data, recv_ns, send_ns = reader.read_next_ext()
    msg = deserialize_message(data, types[topic])
    if topic == "/odom":
        p = msg.pose.pose.position
        if last:
            distance += math.hypot(p.x - last[0], p.y - last[1])
        last = (p.x, p.y)
    else:
        scans += 1
        closest = min(closest, min(r for r in msg.ranges if msg.range_min < r < msg.range_max))

print(f"drove {distance:.2f} m, {scans} scans, closest obstacle {closest:.2f} m")
