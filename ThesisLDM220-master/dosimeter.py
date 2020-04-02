import serialhelper
import error
import Constants


def find_dosimeter(ser):
    while True:
        try:
            dosimeter_id = serialhelper.writer(ser, Constants.WHOCOMMAND)
            dosimeter_id = dosimeter_id[7:13]
            break
        except error.DosimeterNotFound:
            raise error.DosimeterNotFound
    return dosimeter_id


def find_and_convert_value(ser, dosimeter_id):
    comd = Constants.VALUEPREAMBLE + dosimeter_id + \
           Constants.VALUECOMMAND[dosimeter_id.decode()] + Constants.ENDBYTE

    while True:
        try:
            dosimeter_value = serialhelper.writer(ser, comd)
            break
        except error.DosimeterNotFound:
            raise error.DosimeterNotFound

    dosimeter_value = float(
        chr(dosimeter_value[84]) + '.' + dosimeter_value[85:88].decode())
    return dosimeter_value


def FullRun():
    ser = serialhelper.create_serial_connection(Constants.PORT)
    try:
        current_id = find_dosimeter(ser)
        value = find_and_convert_value(ser, current_id)
    except error.DosimeterNotFound:
        raise error.DosimeterNotFound
    ser.close()
    return current_id.decode(), value


