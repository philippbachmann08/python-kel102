import logging

from kel102 import KEL102

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    kel102 = KEL102(port_name="/dev/ttyUSB0", baud_rate=115200, timeout=1)

    current_mode = kel102.get_current_mode()
    load_voltage = kel102.get_load_voltage()
    load_current = kel102.get_load_current()
    load_power = kel102.get_load_power()
