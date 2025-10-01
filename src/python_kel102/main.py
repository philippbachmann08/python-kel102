import logging
import argparse

from kel102 import KEL102, KEL102Mode

def main(port:str)-> None:
    kel102 = KEL102(port=port, baud_rate=115200, timeout=1)

    kel102.get_current_mode()

    kel102.get_load_voltage()
    kel102.get_load_current()
    kel102.get_load_power()

    kel102.get_mode_setting(KEL102Mode.CC)
    kel102.get_mode_setting(KEL102Mode.CV)
    kel102.get_mode_setting(KEL102Mode.CR)
    kel102.get_mode_setting(KEL102Mode.CP)

    kel102.get_mode_setting_min(KEL102Mode.CC)
    kel102.get_mode_setting_min(KEL102Mode.CV)
    kel102.get_mode_setting_min(KEL102Mode.CR)
    kel102.get_mode_setting_min(KEL102Mode.CP)

    kel102.get_mode_setting_max(KEL102Mode.CC)
    kel102.get_mode_setting_max(KEL102Mode.CV)
    kel102.get_mode_setting_max(KEL102Mode.CR)
    kel102.get_mode_setting_max(KEL102Mode.CP)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    parser = argparse.ArgumentParser(
        description="Python control library for the KEL-102 electronic load."
    )
    parser.add_argument(
        "port",
        type=str,
        help="The serial port (e.g., /dev/ttyUSB0 on Linux or COM3 on Windows) for the KEL-102."
    )
    args = parser.parse_args()
    main(args.port)
