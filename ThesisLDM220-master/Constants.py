CURRENTTIMEOUT = 3
PORT = "dev/ttyUSB0"
IP_and_PORT = ("localhost", 8000)

VISIT_DOSAGE_LIMIT = 0.005

WHOCOMMAND = b"\x0A\x30\x31\x30\x46\x30\x30\x33\x37\x0D"
STARTBYTE = b"\x0A"
ENDBYTE = b"\x0D"

DOSIMETER_IDS = ['806142', '806788', "806267","806110", "806061", "805721","805875", "505508", "806265"] #TODO: changed from list to tuple so ids can be added

VALUEPREAMBLE = b"\x0A\x30\x31\x30\x30\x31\x30\x30\x30\x37\x31\x30\x30\x33\x37\x30\x30\x30\x30"

VALUECOMMAND = {'806142': b"\x35\x41\x31\x46", '806788': b"\x41\x36\x33\x30", "806267": b"\x38\x30\x31\x39",
                "806110": b"\x32\x38\x30\x45", "806061": b"\x37\x38\x31\x38", "805721": b"\x32\x46\x32\x33",
                "805875": b"\x38\x34\x32\x31", "805508": b"\x31\x34\x31\x33", "806265": b"\x37\x45\x32\x42"}
