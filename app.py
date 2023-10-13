# coding=UTF-8
# This Python file uses the following encoding: utf-8
import asyncio
import json
import time

from flask import Flask, abort, jsonify, request

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

activeBle = None
num = 0

# 设置ip 和 io uuid
address = "70:04:1D:AE:CB:12"
MAIN_IO_UUID = "0000abf0-0000-1000-8000-00805f9b34fb"
WRITE_IO_UUID = "0000abf1-0000-1000-8000-00805f9b34fb"
READ_IO_UUID = "0000abf2-0000-1000-8000-00805f9b34fb"


def errorCallBack(val):
    print("出错了", val)


services = [
    MAIN_IO_UUID,
    WRITE_IO_UUID,
    READ_IO_UUID,
]


app = Flask(__name__)

"""
Author: zjs
Date: 2023-09-27 18:36:24
Description: 按名称扫描
"""


@app.route("/scanfBleByName")
async def scanfBleByName():
    # 过滤蓝牙
    def filterBle(device: BLEDevice, adv: AdvertisementData):
        preName = request.args.get("name")
        if preName is None:
            preName = "EVA"
        if device.name is None or not device.name.startswith(preName):
            return
        return True

    device: BLEDevice = await BleakScanner.find_device_by_filter(
        filterBle, kwargs={"service_uuids": services}
    )

    return jsonify(
        {
            "data": {
                "name": device.name,
                "address": device.address,
            }
        }
    )


"""
Author: zjs
Date: 2023-09-27 18:36:24
Description: 扫描蓝牙列表
"""


@app.route("/scanfBleList")
async def scanfBle():
    scanfTime = request.args.get("scanfTime")
    if scanfTime is None:
        scanfTime = 5.0
    deviceList = await BleakScanner.discover(
        timeout=float(scanfTime), kwargs={"service_uuids": services}
    )
    result = list(
        filter(
            lambda item: item["name"] != None,
            map(
                lambda el: {
                    "name": el.name,
                    "address": el.address,
                },
                deviceList,
            ),
        )
    )
    return jsonify({"data": result})


"""
Author: zjs
Date: 2023-09-27 18:36:24
Description: 连接蓝牙
"""


@app.route("/connectBle")
async def connectBle():
    uuid = request.args.get("uuid")
    if uuid is None:
        return jsonify({"data": None})
    print(uuid)
    global activeBle
    async with BleakClient(uuid, errorCallBack, services) as client:
        print(client.is_connected)
        activeBle = client

    return jsonify({"data": uuid})

    # try:
    #     client = BleakClient(uuid, errorCallBack, services)
    #     await client.connect()
    #     activeBle = client
    #     print("蓝牙连接成功", uuid)
    # except Exception as e:
    #     print("连接失败", e)
    # finally:
    #     return jsonify({"data": uuid})


"""
Author: zjs
Date: 2023-09-27 18:36:24
Description: 断开连接
"""


@app.route("/disConnectBle")
async def disConnectBle():
    global activeBle
    print(activeBle)
    print(activeBle.is_connected)
    if activeBle is None or not activeBle.is_connected:
        return jsonify({"data": "notConnected"})
    print("准备蓝牙断开连接")
    await activeBle.disconnect()
    print("蓝牙断开连接")
    return jsonify({"data": "ok"})


"""
Author: zjs
Date: 2023-09-27 18:36:24
Description: 写入
"""


@app.route("/writeBle", methods=["POST"])
async def writeBle():
    global activeBle
    if activeBle is None or not activeBle.is_connected:
        abort(400)
    query = json.loads(request.get_data())
    bit = bytes(query["data"])
    await activeBle.write_gatt_char(WRITE_IO_UUID, bit, True)

    return jsonify({"data": "ok"})


"""
Author: zjs
Date: 2023-09-27 18:36:24
Description: 读取
"""


@app.route("/readBle")
async def readBle():
    global activeBle
    if activeBle is None or not activeBle.is_connected:
        abort(400)

    result = await activeBle.read_gatt_char(READ_IO_UUID)
    return jsonify({"data": "result: {0}".format("".join(map(chr, result)))})


@app.route("/getState")
async def getState():
    global activeBle
    if activeBle is None:
        abort(400)
    print()

    return jsonify({"data": True if activeBle.is_connected else False})


async def killBle():
    global activeBle
    if activeBle != None:
        await activeBle.disconnect()


if __name__ == "__main__":
    print("启动在端口10086")
    app.run(host="127.0.0.1", port=10086)
    asyncio.run(killBle(address))
    print("已终结10086端口")


# print("10s number:",num ,"，total",num * 447 ,'bit')
