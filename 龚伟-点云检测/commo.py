# 作者     ：gw
# 创建日期 ：2020-04-09  上午 0:42
# 文件名   ：commo.py

# -*- coding: utf-8 -*-
from queue import Queue
from threading import Condition
import matplotlib.pyplot as plt
a = 1
queue_for_count = Queue()
queue_for_show = Queue()
condition_for_count = Condition()
condition_for_show = Condition()
# fig = plt.figure(figsize=(10, 10))