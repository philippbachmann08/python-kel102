import time
import logging
from enum import Enum
from typing import Optional
from serial import Serial, SerialException

class KEL102Mode(Enum):
    CV = "VOLT"
    CC = "CURR"
    CR = "RES"
    CP = "POW"

def get_mode_unit(mode: KEL102Mode) -> str:
    match mode:
        case KEL102Mode.CV:
            return "V"
        case KEL102Mode.CC:
            return "A"
        case KEL102Mode.CR:
            return "OHM"
        case KEL102Mode.CP:
            return "W"
        case _:
            raise Exception(f"Unknown KEL102Mode {mode}")

class KEL102:
    def __init__(self, port_name: str, baud_rate: int = 115200, timeout: int=1) -> None:
        try:
            self.serial_device = Serial(
                port=port_name,
                baudrate=baud_rate,
                timeout=timeout
            )
            logging.info(f"Successfully connected to {port_name} at {baud_rate} baud.")
        except SerialException as e:
            logging.error(f"Error connecting to {port_name}: {e}")

    def write_and_receive(self, command, receive_delay: float = 0.1) -> Optional[str]:
        _command = f"{command}\r".encode()
        logging.debug(f"Sending command {command}")
        self.serial_device.write(_command)
        time.sleep(receive_delay)
        response = ''
        if self.serial_device.in_waiting:
            response += self.serial_device.read(self.serial_device.in_waiting).decode()
        if response != '':
            logging.debug(f"Received response {response}")
            response = response.lstrip(">").rstrip("\n")
            return response
        return None


    def enable_output(self, enable: bool) -> None:
        value = 'ON' if enable else 'OFF'
        logging.debug(f"Setting output to {value}")
        self.write_and_receive(f":INPut {value}")

    def get_load_current(self) -> float:
        response = self.write_and_receive(":MEASure:CURRent?")
        logging.debug(f"Load current: {response}")
        return float(response.rstrip("A"))

    def get_load_voltage(self) -> float:
        response = self.write_and_receive(":MEASure:VOLTage?")
        logging.debug(f"Load voltage: {response}")
        return float(response.rstrip("V"))

    def get_load_power(self) -> float:
        response = self.write_and_receive(":MEASure:POWer?")
        logging.debug(f"Load power: {response}")
        return float(response.rstrip("W"))

    def get_current_mode(self) -> KEL102Mode:
        response = self.write_and_receive(":FUNCtion?")
        current_mode = KEL102Mode(response)
        logging.debug(f"Current mode: {current_mode.name}")
        return current_mode

    def set_current_mode(self, mode: KEL102Mode) -> None:
        logging.debug(f"Setting mode to {mode.name}")
        self.write_and_receive(f":FUNCtion {mode.value}")

    def get_mode_setting(self, mode: KEL102Mode) -> float:
        response = self.write_and_receive(f":{mode.value}?")
        logging.debug(f"Current {mode.name} setting: {response}")
        return float(response.rstrip(get_mode_unit(mode)))

    def set_mode_setting(self, mode: KEL102Mode, value: float)-> None:
        unit = get_mode_unit(mode)
        logging.debug(f"Setting {mode.name} to {value}{unit}")
        self.write_and_receive(f":{mode.value} {value}{unit}")

    def get_mode_setting_min(self, mode: KEL102Mode)-> float:
        response = self.write_and_receive(f":{mode.value}:LOWer?")
        logging.debug(f"Minimal allowed {mode.name} value: {response}")
        return float(response.rstrip(get_mode_unit(mode)))

    def get_mode_setting_max(self, mode: KEL102Mode) -> float:
        response = self.write_and_receive(f":{mode.value}:UPPer?")
        logging.debug(f"Maximum allowed {mode.name} value: {response}")
        return float(response.rstrip(get_mode_unit(mode)))







