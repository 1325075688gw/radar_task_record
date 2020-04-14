import struct
import math
import numpy as np
import serial
import os
import time
import binascii
import json
import threading
import ctypes
import inspect
import sys

from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock, Condition
from collections import OrderedDict
from queue import Queue
from copy import deepcopy


sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\杨家辉-点云聚类")
sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\郭泽中-跟踪、姿态识别")
import analyze_radar_data
import commo

queue_for_calculate_transfer = Queue()
queue_for_calculate_not_transfer = Queue()

tlv = "2I"
tlv_struct = struct.Struct(tlv)
tlv_size = tlv_struct.size

frame_header = "Q9I2H"
frame_header_struct = struct.Struct(frame_header)
frame_header_size = frame_header_struct.size

point_unit = "5f"
point_unit_struct = struct.Struct(point_unit)
point_unit_size = point_unit_struct.size

point = "2bh2H"
point_struct = struct.Struct(point)
point_size = point_struct.size

target_index = "B"
target_index_struct = struct.Struct(target_index)
target_index_size = target_index_struct.size

target_list = "I9f"
target_list_struct = struct.Struct(target_list)
target_list_size = target_list_struct.size


class Point:
    def __init__(self, pid, x, y, z, dopper, snr):
        self.pid = pid
        self.x = x
        self.y = y
        self.z = z
        self.dopper = dopper
        self.snr = snr


class RawPoint:
    def __init__(self, pid, azi, elev, range, doppler, snr):
        self.pid = pid
        self.azi = azi
        self.elev = elev
        self.range = range
        self.doppler = doppler
        self.snr = snr


class uartParserSDK():
    def __init__(self, data_port="COM4", user_port="COM3"):
        self.json_data_not_transfer = OrderedDict()
        self.json_data_transfer = OrderedDict()
        self.magic_word = 0x708050603040102
        self.bytes_data = bytes(1)
        self.max_points = 500
        self.polar = np.zeros((5, self.max_points))
        self.cart_transfer = np.zeros((5, self.max_points))
        self.cart_not_transfer = np.zeros((5, self.max_points))
        self.detected_target_num = 0
        self.detected_point_num = 0
        self.target_list = np.ones((10, 20)) * (-1)
        self.target_index = np.zeros((1, self.max_points))
        self.fail = 0
        self.indexes = []
        self.unique = []
        self.frame_num = 0
        self.bytes_num = 4666
        self.tlv_header_length = 8
        self.header_length = 48
        self.save_points_th = Thread()
        self.receive_data_th = 0
        self.flag = 1
        self.missed_frame_num = 0
        self.theta = math.radians(17)
        self.theta_diff = math.radians(90-17)
        self.theta_30 = math.radians(30)
        self.theta_15 = math.radians(15)
        self.radar_z = 1.75

        '''
        port=串口号, 
        baudrate=波特率, 
        bytesize=数据位, 
        stopbits=停止位, 
        parity=校验位
        '''
        self.user_port = serial.Serial(user_port, 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                       timeout=0.3)
        self.data_port = serial.Serial(data_port, 921600 * 2, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                       timeout=0.025)

    def open_port(self):
        if self.data_port.isOpen():
            self.data_port.reset_output_buffer()
            print("数据串口打开成功！")
        else:
            print("数据串口打开失败！")

        if self.user_port.isOpen():
            self.user_port.reset_input_buffer()
            print("用户串口打开成功！")
        else:
            print("用户串口打开失败！")

    def send_config(self):
        current_dir = os.path.dirname(__file__)
        file = open(current_dir + "/ODS_6m_default.cfg", "r+")
        if file is None:
            print("配置文件不存在!")
            return
        for text in file.readlines():
            print("send config:" + text)
            self.user_port.write(text.encode('utf-8'))
            self.user_port.write('\n'.encode('utf-8'))
            time.sleep(0.2)
        file.close()

    def receive_data_thread(self):
        self.receive_data_th = Thread(target=self.receive_data)
        return self.receive_data_th

    def receive_data(self):
        while self.flag:
            # start_time = time.time() * 1000
            data = self.data_port.read(self.bytes_num)
            # end_time = time.time() * 1000
            # print("read一帧需要:{0}".format(end_time - start_time))
            # start_time = time.time() * 1000
            self.bytes_data += data
            self.bytes_data = self.get_frame(self.bytes_data)
            # print("当前帧数：{0}".format(self.frame_num))
            # end_time = time.time() * 1000
            # print("解析一帧需要:{0}\n".format(end_time - start_time))

    def put_queue_thread(self):
        self.put_queue_th = Thread(target=self.put_queue)
        return self.put_queue_th

    def put_queue(self):
        while self.flag:
            # print("queue_for_calculate长度:{0}".format(queue_for_calculate.qsize()))
            """
            point_cloud_num = 0
            point_cloud_list = []
            cart_transfer = queue_for_calculate_transfer.get().transpose()
            for index, value in enumerate(cart_transfer):
                # raw_point = RawPoint(index+1, value[0], value[1], value[2], value[3], value[4]).__dict__
                point = Point(index + 1, value[0], value[1], value[2], value[3], value[4]).__dict__
                point_cloud_list.append(point)
                point_cloud_num += 1
            temp = dict()
            t = time.time() * 1000
            temp["frame_num"] = self.frame_num
            temp["time_stamp"] = int(round(t))
            temp["point_num"] = point_cloud_num
            temp["point_list"] = point_cloud_list
            frame_num = "frame_num_" + str(self.frame_num)
            # print("\nlen(value)：{0}".format(self.frame_num))
            frame_dict = {frame_num: temp}
            self.json_data_transfer.update(frame_dict)
            # with commo.condition_for_count:
            # print("queue_for_count_receive_uart:{0}".format(commo.queue_for_count.qsize()))
            # print("frame_num:{0}".format(self.frame_num))
            commo.queue_for_count_transfer.put(temp)
            """

            point_cloud_num = 0
            point_cloud_list = []
            cart_not_transfer = queue_for_calculate_not_transfer.get().transpose()
            for index, value in enumerate(cart_not_transfer):
                # raw_point = RawPoint(index+1, value[0], value[1], value[2], value[3], value[4]).__dict__
                point = Point(index + 1, value[0], value[1], value[2], value[3], value[4]).__dict__
                point_cloud_list.append(point)
                point_cloud_num += 1
            temp = dict()
            t = time.time() * 1000
            temp["frame_num"] = self.frame_num
            temp["time_stamp"] = int(round(t))
            temp["point_num"] = point_cloud_num
            temp["point_list"] = point_cloud_list
            frame_num = "frame_num_" + str(self.frame_num)
            # print("\nlen(value)：{0}".format(self.frame_num))
            frame_dict = {frame_num: temp}
            self.json_data_not_transfer.update(frame_dict)
            # with commo.condition_for_count:
            # print("queue_for_count_receive_uart:{0}".format(commo.queue_for_count.qsize()))
            # print("frame_num:{0}".format(self.frame_num))
            commo.queue_for_count_not_transfer.put(temp)

            # commo.condition_for_count.notify_all()
            # commo.condition_for_count.wait()

            if self.frame_num == 10000:
                with open("new_points_not_transfer.json", "w") as file:
                    json.dump(self.json_data_not_transfer, file)
                with open("new_points_transfer.json", "w") as file:
                    json.dump(self.json_data_transfer, file)
                self.flag = 0
                print("丢失{0}帧 ".format(self.missed_frame_num))
                exit()

    def show_frame(self):
        time.sleep(3)
        self.cluster_points_thread().start()
        self.show_cluster_tracker_thread().start()

    def cluster_points_thread(self):
        cluster_points_th = Thread(target=analyze_radar_data.cluster_points)
        return cluster_points_th

    def show_cluster_tracker_thread(self):
        show_cluster_tracker_th = Thread(target=analyze_radar_data.show_cluster_tracker)
        return show_cluster_tracker_th

    def get_frame(self, data_in):
        self.polar = np.zeros((5, self.max_points))
        self.cart_transfer = np.zeros((5, self.max_points))
        self.cart_not_transfer = np.zeros((5, self.max_points))
        self.target = np.zeros((10, 20))
        self.detected_target_num = 0
        self.detected_point_num = 0
        while 1:
            try:
                magic, version, packet_length, plat_form, \
                frame_num, sub_frame_num, chirp_margin, frame_margin, \
                track_process_time, uart_sent_time, num_tlvs, checksum = \
                    frame_header_struct.unpack_from(data_in)
            except:
                self.fail = 1
                return data_in
            if magic != self.magic_word:
                data_in = data_in[1:]
            else:
                break
        if (self.frame_num + 1 != frame_num):
            self.missed_frame_num += 1
        self.frame_num = frame_num
        data_in = data_in[self.header_length:]
        left_data = packet_length - len(data_in) - self.header_length
        # remainingData 大于0，说明该帧数据没接收完
        count = 0
        while left_data > 0 and count <= 3:
            new_data = self.data_port.read(left_data)
            left_data = packet_length - len(data_in) - self.header_length - len(new_data)
            data_in += new_data

        for i in range(num_tlvs):
            # decode People Counting TLV Header
            try:
                tlv_type, tlv_length = self.parse_tlv_header(data_in)
                data_in = data_in[self.tlv_header_length:]
                data_length = tlv_length - self.tlv_header_length
                if tlv_type == 6:
                    # point cloud
                    self.parse_point(data_in, data_length)
                elif tlv_type == 7:
                    # target list
                    self.parse_target_list(data_in, data_length)
                elif (tlv_type == 8):
                    # target index
                    self.parse_target_index(data_in, data_length)
                data_in = data_in[data_length:]
            except Exception as e:
                print("解析头出错：{0}".format(e))
        return data_in

    def parse_tlv_header(self, data_in):
        tlv_type, tlv_length = tlv_struct.unpack_from(data_in)
        return tlv_type, tlv_length

    def parse_point(self, data_in, data_length):
        point_unit = point_unit_struct.unpack_from(data_in)
        data_in = data_in[point_unit_size:]
        self.detected_point_num = int((data_length - point_unit_size) / point_size)

        for i in range(self.detected_point_num):
            try:
                elev, azi, doppler, ran, snr = point_struct.unpack_from(data_in)
                data_in = data_in[point_size:]
                # range
                self.polar[0, i] = ran * point_unit[3]
                if azi >= 128:
                    azi -= 256
                if elev >= 128:
                    elev -= 256
                if doppler >= 65536:
                    doppler -= 65536
                # azi
                self.polar[1, i] = azi * point_unit[1]
                # elev
                self.polar[2, i] = elev * point_unit[0]
                # doppler
                self.polar[3, i] = doppler * point_unit[2]
                # snr
                self.polar[4, i] = snr * point_unit[4]
            except:
                self.detected_point_num = i
                break
        self.polar_to_cart()
    def polar_to_cart(self):
        self.cart_transfer = np.empty((5, self.detected_point_num))
        self.cart_not_transfer = np.empty((5, self.detected_point_num))
        for i in range(0, self.detected_point_num):
            # x
            self.cart_not_transfer[0, i] = self.polar[0, i] * math.cos(self.polar[2, i]) * math.sin(self.polar[1, i])
            # y
            self.cart_not_transfer[1, i] = self.polar[0, i] * math.cos(self.polar[2, i]) * math.cos(self.polar[1, i])
            # z
            self.cart_not_transfer[2, i] = self.polar[0, i] * math.sin(self.polar[2, i])

            # x
            self.cart_transfer[0, i] = self.polar[0, i] * math.cos(self.theta - self.polar[2, i] + self.theta_15) * math.sin(self.polar[1, i] - self.theta_30)
            # y
            self.cart_transfer[1, i] = self.polar[0, i] * math.cos(self.theta - self.polar[2, i] + self.theta_15) * math.cos(self.polar[1, i] - self.theta_30)
            # z
            self.cart_transfer[2, i] = self.radar_z - self.polar[0, i] * math.sin(self.theta - self.polar[2, i] + self.theta_15)
        self.cart_transfer[3, :] = self.polar[3, 0:self.detected_point_num]
        self.cart_transfer[4, :] = self.polar[4, 0:self.detected_point_num]

        self.cart_not_transfer[3, :] = self.polar[3, 0:self.detected_point_num]
        self.cart_not_transfer[4, :] = self.polar[4, 0:self.detected_point_num]
        queue_for_calculate_transfer.put(deepcopy(self.cart_transfer))
        queue_for_calculate_not_transfer.put(deepcopy(self.cart_not_transfer))

    def parse_target_list(self, data_in, data_length):
        self.detected_target_num = int(data_length / target_list_size)
        target_list = np.empty((13, self.detected_target_num))
        for i in range(self.detected_target_num):
            target_data = target_list_struct.unpack_from(data_in)
            # tid, posx, posy
            target_list[0:3, i] = target_data[0:3]
            # posz
            target_list[3, i] = target_data[7]
            # evlx, evly
            target_list[4:6, i] = target_data[3:5]
            # evlz
            target_list[6, i] = target_data[8]
            # accx, accy
            target_list[7:9, i] = target_data[5:7]
            # accz
            target_list[9, i] = target_data[9]
            target_list[10:13, i] = [0, 0, 0]
            data_in = data_in[target_list_size:]
        self.target_list = target_list

    def parse_target_index(self, data_in, data_length):
        self.detected_target_num = int(data_length / target_index_size)
        self.target_index = []
        for i in range(self.detected_target_num):
            index = target_index_struct.unpack_from(data_in)
            data_in = data_in[target_index_size:]
            self.target_index.append(index[0])

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

if __name__ == "__main__":
    uart_parse_sdk_instance = uartParserSDK("COM4", "COM3")
    uart_parse_sdk_instance.open_port()
    uart_parse_sdk_instance.send_config()
    uart_parse_sdk_instance.receive_data_thread().start()
    uart_parse_sdk_instance.put_queue_thread().start()
    uart_parse_sdk_instance.show_frame()