import pytest

from python_kel102.kel102 import KEL102, KEL102Mode


@pytest.fixture
def mocked_serial_device(mocker):
    mocked_serial_device = mocker.Mock()
    mocked_serial = mocker.Mock(return_value=mocked_serial_device)
    mocker.patch("python_kel102.kel102.Serial", mocked_serial)
    return mocked_serial_device


def test_init_serial(mocked_serial_device):
    kel102 = KEL102("test")

    assert kel102.serial_device == mocked_serial_device

def test_serial_send_and_receive_empty(mocked_serial_device):
    mocked_serial_device.in_waiting = 0
    kel102 = KEL102("test")

    result = kel102.write_and_receive("data", 0.1)

    mocked_serial_device.write.assert_called_once_with("data\r".encode())
    assert result is None

def test_serial_send_and_receive_data(mocked_serial_device, mocker):
    mocked_serial_device.in_waiting = 6
    mocked_serial_device.read = mocker.Mock(side_effect=[b">test\n"])
    kel102 = KEL102("test")

    result = kel102.write_and_receive("data", 0.1)

    mocked_serial_device.write.assert_called_once_with("data\r".encode())
    assert result == "test"

@pytest.mark.parametrize(
    "enable, expected_command",
    [
        (True,b":INPut ON\r"),
         (False,b":INPut OFF\r")
    ]
)
def test_set_output(mocked_serial_device, enable, expected_command):
    mocked_serial_device.in_waiting = 0
    kel102 = KEL102("test")

    kel102.enable_output(enable)

    mocked_serial_device.write.assert_called_once_with(expected_command)

def test_get_load_current(mocked_serial_device, mocker):
    mocked_serial_device.in_waiting = 8
    mocked_serial_device.read = mocker.Mock(side_effect=[b">0.789A\n"])
    kel102 = KEL102("test")

    load_current = kel102.get_load_current()

    mocked_serial_device.write.assert_called_once_with(":MEASure:CURRent?\r".encode())
    assert load_current == 0.789

def test_get_load_voltage(mocked_serial_device, mocker):
    mocked_serial_device.in_waiting = 8
    mocked_serial_device.read = mocker.Mock(side_effect=[b">1.4999V\n"])
    kel102 = KEL102("test")

    load_voltage = kel102.get_load_voltage()

    mocked_serial_device.write.assert_called_once_with(":MEASure:VOLTage?\r".encode())
    assert load_voltage == 1.4999

def test_get_load_power(mocked_serial_device, mocker):
    mocked_serial_device.in_waiting = 8
    mocked_serial_device.read = mocker.Mock(side_effect=[b">1.1968W\n"])
    kel102 = KEL102("test")

    load_power = kel102.get_load_power()

    mocked_serial_device.write.assert_called_once_with(":MEASure:POWer?\r".encode())
    assert load_power == 1.1968

@pytest.mark.parametrize(
    "response, expected_mode",
    [
        (b">VOLT\n", KEL102Mode.CV),
        (b">CURR\n", KEL102Mode.CC),
        (b">RES\n", KEL102Mode.CR),
        (b">POW\n", KEL102Mode.CP),
     ]
)
def test_get_current_mode(mocked_serial_device, mocker, response, expected_mode):
    mocked_serial_device.in_waiting = 8
    mocked_serial_device.read = mocker.Mock(return_value=response)
    kel102 = KEL102("test")

    current_mode = kel102.get_current_mode()

    mocked_serial_device.write.assert_called_once_with(":FUNCtion?\r".encode())
    assert current_mode == expected_mode

@pytest.mark.parametrize(
    "mode, expected_command",
    [
        (KEL102Mode.CV, b":FUNCtion VOLT\r"),
        (KEL102Mode.CC, b":FUNCtion CURR\r"),
        (KEL102Mode.CR, b":FUNCtion RES\r"),
        (KEL102Mode.CP, b":FUNCtion POW\r"),
     ]
)
def test_set_current_mode(mocked_serial_device, mocker, mode, expected_command):
    mocked_serial_device.in_waiting = 0
    kel102 = KEL102("test")

    kel102.set_current_mode(mode)

    mocked_serial_device.write.assert_called_once_with(expected_command)

@pytest.mark.parametrize(
    "mode, expected_command, response, expected_result",
    [
        (KEL102Mode.CV, b":VOLT?\r", b">4.123V\n", 4.123),
        (KEL102Mode.CC, b":CURR?\r", b">1.142A\n", 1.142),
        (KEL102Mode.CR, b":RES?\r", b">200.4OHM\n", 200.4),
        (KEL102Mode.CP, b":POW?\r", b">3.41W\n", 3.41),
     ]
)
def test_get_mode_setting(mocked_serial_device, mocker, mode, expected_command, response, expected_result):
    mocked_serial_device.in_waiting = len(response)
    mocked_serial_device.read = mocker.Mock(return_value=response)
    kel102 = KEL102("test")

    result = kel102.get_mode_setting(mode)

    mocked_serial_device.write.assert_called_once_with(expected_command)
    assert result == expected_result

@pytest.mark.parametrize(
    "mode, value, expected_command",
    [
        (KEL102Mode.CV, 5.1, b":VOLT 5.1V\r"),
        (KEL102Mode.CC, 2.2, b":CURR 2.2A\r",),
        (KEL102Mode.CR, 202.1, b":RES 202.1OHM\r"),
        (KEL102Mode.CP, 4.12, b":POW 4.12W\r"),
     ]
)
def test_set_mode_setting(mocked_serial_device, mode, value, expected_command):
    mocked_serial_device.in_waiting = 0
    kel102 = KEL102("test")

    result = kel102.set_mode_setting(mode, value)

    mocked_serial_device.write.assert_called_once_with(expected_command)

@pytest.mark.parametrize(
    "mode, expected_command, response, expected_result",
    [
        (KEL102Mode.CV, b":VOLT:LOWer?\r", b">0.2V\n", 0.2),
        (KEL102Mode.CC, b":CURR:LOWer?\r", b">0.01A\n", 0.01),
        (KEL102Mode.CR, b":RES:LOWer?\r", b">0.5OHM\n", 0.5),
        (KEL102Mode.CP, b":POW:LOWer?\r", b">0.2W\n", 0.2),
     ]
)
def test_get_mode_setting_minimum(mocked_serial_device, mocker, mode, expected_command, response, expected_result):
    mocked_serial_device.in_waiting = len(response)
    mocked_serial_device.read = mocker.Mock(return_value=response)
    kel102 = KEL102("test")

    result = kel102.get_mode_setting_min(mode)

    mocked_serial_device.write.assert_called_once_with(expected_command)
    assert result == expected_result

@pytest.mark.parametrize(
    "mode, expected_command, response, expected_result",
    [
        (KEL102Mode.CV, b":VOLT:UPPer?\r", b">20.1V\n", 20.1),
        (KEL102Mode.CC, b":CURR:UPPer?\r", b">10.2\n", 10.2),
        (KEL102Mode.CR, b":RES:UPPer?\r", b">1000.50OHM\n", 1000.50),
        (KEL102Mode.CP, b":POW:UPPer?\r", b">33.3W\n", 33.3),
     ]
)
def test_get_mode_setting_maximum(mocked_serial_device, mocker, mode, expected_command, response, expected_result):
    mocked_serial_device.in_waiting = len(response)
    mocked_serial_device.read = mocker.Mock(return_value=response)
    kel102 = KEL102("test")

    result = kel102.get_mode_setting_max(mode)

    mocked_serial_device.write.assert_called_once_with(expected_command)
    assert result == expected_result