#Author: ProgrammerHasan
#Web: https://programmerhasan.com
#web: https://mehedihasan.dev

import sys
import requests
from easymodbus.modbusClient import *


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    timer = threading.Timer(sec, func_wrapper)
    timer.start()
    return timer


client = ModbusClient('WW2')
client.baudrate = 9600
client.parity = Parity.none
client.stopbits = Stopbits.one

client.connect()

registerAddress = 0


def read():
    input_register = client.read_holdingregisters(registerAddress, 8)
    print(input_register)

    # Store in Server
    try:
        channel_1_decimal = str(input_register[0])
        channel_1_decimal_prefix_zero_count = 5 - len(channel_1_decimal)
        for i in range(channel_1_decimal_prefix_zero_count):
            channel_1_decimal = '0' + channel_1_decimal

        response = requests.api.post("yourSensorDataReadingApi", {
            'sensor_uuid': 'your_sensor_uuid',
            'sensor_data': str(input_register[1]) + '.' + channel_1_decimal,
        })

        channel_2_decimal = str(input_register[2])
        channel_2_decimal_prefix_zero_count = 5 - len(channel_2_decimal)
        for i in range(channel_2_decimal_prefix_zero_count):
            channel_2_decimal = '0' + channel_2_decimal

        response = requests.api.post("yourSensorDataReadingApi", {
            'sensor_uuid': 'your_sensor_uuid',
            'sensor_data': str(input_register[3]) + '.' + channel_2_decimal,
        })
    except Exception as e:
        print(e)
        print('Server Problem! Cannot Upload Data to Server:) Please Contact Your Admin.')
        pass


read()

set_interval(read, 2)


def exit_application():
    print("Exiting Application...")
    client.close()
    sys.exit(0)

