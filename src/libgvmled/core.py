import binascii
import socket
import time


from crc16 import crc16xmodem


GVM_RGB_LED_TYPE = 48
MAGIC_STRING = "4C5409"
MAGIC_NUMBER = "57000"
MESSAGE_TEMPLATE = f"{MAGIC_STRING}{{device_id:02x}}{{device_type:02x}}" \
                   f"{MAGIC_NUMBER}"\
                   f"{{command:01x}}01{{parameter:02x}}"
CMD_POWER = 0
CMD_BRIGHTNESS = 2
CMD_CCT = 3
CMD_HUE = 4
CMD_SATURATION = 5
PRM_POWER_ON = 1
PRM_POWER_OFF = 0


class GVMLamp(object):
    def __init__(
            self,
            channel,
            gvm_type=GVM_RGB_LED_TYPE,
            destination_ip='255.255.255.255',
            destination_port=2525,
            sleep=2,
            verbose=False,
            *args, **kwargs):
        super(GVMLamp, self).__init__(*args, **kwargs)
        self.channel = channel
        self.gvm_type = gvm_type
        self.led_endpoint = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.led_endpoint.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.verbose = verbose
        self.sleep = sleep

    def send_message(self, command, parameter):
        command_message = MESSAGE_TEMPLATE.format(
            device_id=self.channel,
            device_type=self.gvm_type,
            command=command,
            parameter=parameter
        )

        bytes_message = binascii.unhexlify(command_message)
        crc_result = crc16xmodem(bytes_message)

        final_message = "{0}{1:04x}".format(command_message, crc_result).upper()
        if self.verbose:
            print("Trying Msg: {} \t DeviceID: {} \t Device Type: {}".format(
                final_message,
                self.channel,
                self.gvm_type
            ))

        self.led_endpoint.sendto(
            bytes(final_message, 'utf-8'),
            (self.destination_ip, self.destination_port)
        )
        time.sleep(self.sleep)

    def turn_off(self):
        self.send_message(CMD_POWER, PRM_POWER_OFF)

    def turn_on(self):
        self.send_message(CMD_POWER, PRM_POWER_ON)

    def set_brightness(self, level):
        self.send_message(CMD_BRIGHTNESS, level % 101)

    def set_cct(self, level):
        self.send_message(CMD_CCT, level % 101)

    def set_hue(self, hue):
        self.send_message(CMD_HUE, hue % 84)

    def set_saturation(self, level):
        self.send_message(CMD_SATURATION, level % 101)

    def do_hue_cycle(self, exit_func=lambda x: False):
        self.set_brightness(50)
        self.set_saturation(100)

        i = 0
        while exit_func(self) is False:
            self.set_hue(i)
            i += 1
            if i == 84:
                i = 0
