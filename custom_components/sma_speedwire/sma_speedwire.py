
import time
from struct import *
import socket
import logging

MY_SYSTEMID    = 0x00ED                # random number, has to be different from any device in local network
MY_SERIAL      = 0x23021922            # random number, has to be different from any device in local network
ANY_SYSTEMID   = 0xFFFF                # 0xFFFF is any susyid
ANY_SERIAL     = 0xFFFFFFFF            # 0xFFFFFFFF is any serialnumber
SMA_PKT_HEADER = "534D4100000402A000000001"
SMA_ESIGNATURE = "00106065"

# UDP_IPB = "239.12.255.254"
# MESSAGE = bytes.fromhex('534d4100000402a0ffffffff0000002000000000')

COMMAND_LIST = {
    # name,           [command,    first,      last      ]
    "login":          [0xFFFD040C, 0x00000007, 0x00000384],
    "logout":         [0xFFFD010E, 0xFFFFFFFF, 0x00000000],
    "info":           [0x58000200, 0x00821E00, 0x008220FF],
    "energy":         [0x54000200, 0x00260100, 0x002622FF],
    "power_ac_total": [0x51000200, 0x00263F00, 0x00263FFF],
}

SMA_INV_TYPE = {
    0000: "Unknown Inverter Type",
    9015: "SB 700",
    9016: "SB 700U",
    9017: "SB 1100",
    9018: "SB 1100U",
    9019: "SB 1100LV",
    9020: "SB 1700",
    9021: "SB 1900TLJ",
    9022: "SB 2100TL",
    9023: "SB 2500",
    9024: "SB 2800",
    9025: "SB 2800i",
    9026: "SB 3000",
    9027: "SB 3000US",
    9028: "SB 3300",
    9029: "SB 3300U",
    9030: "SB 3300TL",
    9031: "SB 3300TL HC",
    9032: "SB 3800",
    9033: "SB 3800U",
    9034: "SB 4000US",
    9035: "SB 4200TL",
    9036: "SB 4200TL HC",
    9037: "SB 5000TL",
    9038: "SB 5000TLW",
    9039: "SB 5000TL HC",
    9066: "SB 1200",
    9067: "STP 10000TL-10",
    9068: "STP 12000TL-10",
    9069: "STP 15000TL-10",
    9070: "STP 17000TL-10",
    9084: "WB 3600TL-20",
    9085: "WB 5000TL-20",
    9086: "SB 3800US-10",
    9098: "STP 5000TL-20",
    9099: "STP 6000TL-20",
    9100: "STP 7000TL-20",
    9101: "STP 8000TL-10",
    9102: "STP 9000TL-20",
    9103: "STP 8000TL-20",
    9104: "SB 3000TL-JP-21",
    9105: "SB 3500TL-JP-21",
    9106: "SB 4000TL-JP-21",
    9107: "SB 4500TL-JP-21",
    9108: "SCSMC",
    9109: "SB 1600TL-10",
    9131: "STP 20000TL-10",
    9139: "STP 20000TLHE-10",
    9140: "STP 15000TLHE-10",
    9157: "Sunny Island 2012",
    9158: "Sunny Island 2224",
    9159: "Sunny Island 5048",
    9160: "SB 3600TL-20",
    9168: "SC630HE-11",
    9169: "SC500HE-11",
    9170: "SC400HE-11",
    9171: "WB 3000TL-21",
    9172: "WB 3600TL-21",
    9173: "WB 4000TL-21",
    9174: "WB 5000TL-21",
    9175: "SC 250",
    9176: "SMA Meteo Station",
    9177: "SB 240-10",
    9171: "WB 3000TL-21",
    9172: "WB 3600TL-21",
    9173: "WB 4000TL-21",
    9174: "WB 5000TL-21",
    9179: "Multigate-10",
    9180: "Multigate-US-10",
    9181: "STP 20000TLEE-10",
    9182: "STP 15000TLEE-10",
    9183: "SB 2000TLST-21",
    9184: "SB 2500TLST-21",
    9185: "SB 3000TLST-21",
    9186: "WB 2000TLST-21",
    9187: "WB 2500TLST-21",
    9188: "WB 3000TLST-21",
    9189: "WTP 5000TL-20",
    9190: "WTP 6000TL-20",
    9191: "WTP 7000TL-20",
    9192: "WTP 8000TL-20",
    9193: "WTP 9000TL-20",
    9254: "Sunny Island 3324",
    9255: "Sunny Island 4.0M",
    9256: "Sunny Island 4248",
    9257: "Sunny Island 4248U",
    9258: "Sunny Island 4500",
    9259: "Sunny Island 4548U",
    9260: "Sunny Island 5.4M",
    9261: "Sunny Island 5048U",
    9262: "Sunny Island 6048U",
    9278: "Sunny Island 3.0M",
    9279: "Sunny Island 4.4M",
    9281: "STP 10000TL-20",
    9282: "STP 11000TL-20",
    9283: "STP 12000TL-20",
    9284: "STP 20000TL-30",
    9285: "STP 25000TL-30",
    9301: "SB1.5-1VL-40",
    9302: "SB2.5-1VL-40",
    9303: "SB2.0-1VL-40",
    9304: "SB5.0-1SP-US-40",
    9305: "SB6.0-1SP-US-40",
    9306: "SB8.0-1SP-US-40",
    9307: "Energy Meter",
    9313: "SB50.0-3SP-40",
    9319: "SB3.0-1AV-40 (Sunny Boy 3.0 AV-40)",
    9320: "SB3.6-1AV-40 (Sunny Boy 3.6 AV-40)",
    9321: "SB4.0-1AV-40 (Sunny Boy 4.0 AV-40)",
    9322: "SB5.0-1AV-40 (Sunny Boy 5.0 AV-40)",
    9324: "SBS1.5-1VL-10 (Sunny Boy Storage 1.5)",
    9325: "SBS2.0-1VL-10 (Sunny Boy Storage 2.0)",
    9326: "SBS2.5-1VL-10 (Sunny Boy Storage 2.5)",
    9327: "SMA Energy Meter",
    9331: "SI 3.0M-12 (Sunny Island 3.0M)",
    9332: "SI 4.4M-12 (Sunny Island 4.4M)",
    9333: "SI 6.0H-12 (Sunny Island 6.0H)",
    9334: "SI 8.0H-12 (Sunny Island 8.0H)",
    9335: "SMA Com Gateway",
    9336: "STP 15000TL-30",
    9337: "STP 17000TL-30",
    9344: "STP4.0-3AV-40 (Sunny Tripower 4.0)",
    9345: "STP5.0-3AV-40 (Sunny Tripower 5.0)",
    9346: "STP6.0-3AV-40 (Sunny Tripower 6.0)",
    9347: "STP8.0-3AV-40 (Sunny Tripower 8.0)",
    9348: "STP10.0-3AV-40 (Sunny Tripower 10.0)",
    9356: "SBS3.7-1VL-10 (Sunny Boy Storage 3.7)",
    9358: "SBS5.0-10 (Sunny Boy Storage 5.0)",
    9359: "SBS6.0-10 (Sunny Boy Storage 6.0)",
    9366: "STP3.0-3AV-40 (Sunny Tripower 3.0)",
    9401: "SB3.0-1AV-41 (Sunny Boy 3.0 AV-41)",
    9402: "SB3.6-1AV-41 (Sunny Boy 3.6 AV-41)",
    9403: "SB4.0-1AV-41 (Sunny Boy 4.0 AV-41)",
    9404: "SB5.0-1AV-41 (Sunny Boy 5.0 AV-41)",
    9405: "SB6.0-1AV-41 (Sunny Boy 6.0 AV-41)",
}

SMA_INV_CLASS = {
    8000: "Any Device",
    8001: "Solar Inverter",
    8002: "Wind Turbine Inverter",
    8007: "Batterie Inverter",
    8033: "Consumer",
    8064: "Sensor System in General",
    8065: "Electricity meter",
    8128: "Communication product",
}

class smaError(Exception):
    pass

class SMA_SPEEDWIRE:
    def __init__(self, host, password="0000", logger=None):
        self.host = host
        self.port = 9522
        self.password = password
        self.pkt_id = 0
        self.my_id = MY_SYSTEMID.to_bytes(2, byteorder='little') + MY_SERIAL.to_bytes(4, byteorder='little')
        self.target_id = ANY_SYSTEMID.to_bytes(2, byteorder='little') + ANY_SERIAL.to_bytes(4, byteorder='little')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(3.0)
        self.retry = 2

        self.serial = None
        self.inv_class = None
        self.inv_type = None
        self.sensors = {
            "energy_total":   {"name":"Energy Production Total","value":None,"unit":"kWh"},
            "energy_today":   {"name":"Energy Production Today","value":None,"unit":"kWh"},
            "power_ac_total": {"name":"Power Production Now","value":None,"unit":"W"},
        }

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        
    def _packet(self, cmd):
        self.pkt_id += 1                                                                                # increase packet counter
        commands = COMMAND_LIST[cmd]
        sep2 = bytes([0x00, 0x00])                                                                      # separator for default commands
        sep4 = bytes([0x00, 0x00, 0x00, 0x00])
        data = sep4                                                                                     # data same as separator4
        esignature = bytes.fromhex(SMA_ESIGNATURE + "09A0")

        if cmd == "login":
            sep2 = bytes([0x00, 0x01])                                                                  # separator for login
            esignature = bytes.fromhex(SMA_ESIGNATURE + "0EA0")
            encpasswd = [0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88]
            encpasswd[0:len(self.password)] = [((0x88 + ord(char)) & 0xff) for char in self.password]   # encode password
            data = int(time.time()).to_bytes(4, byteorder='little')                                     # timestamp utc
            data += sep4 + bytes(encpasswd) + sep4                                                      # setarator4 + password + setarator4
        elif cmd == "logout":
            sep2 = bytes([0x00, 0x03])                                                                  # separator for logout
            esignature = bytes.fromhex(SMA_ESIGNATURE + "08A0")
            data = bytes([])                                                                            # no data on logout

        msg = bytes.fromhex(SMA_PKT_HEADER) + bytes([0x00, 0x00]) + esignature                          # header + placeholder len + signature
        msg += self.target_id + sep2 + self.my_id + sep2                                                # targets and my address
        msg += sep4 + (self.pkt_id | 0x8000).to_bytes(2, byteorder='little')                            # packet counter
        msg += commands[0].to_bytes(4, byteorder='little')                                              # command + first + last
        msg += commands[1].to_bytes(4, byteorder='little')
        msg += commands[2].to_bytes(4, byteorder='little')
        msg += data                                                                                     # data
        pkt_len = (len(msg)-20).to_bytes(2, byteorder='big')                                            # calculate packet length
        msg = msg[:12] + pkt_len + msg[14:]                                                             # insert packet length

        self.logger.debug("> %s", msg.hex())
        return msg

    def _send_recieve(self, cmd, receive=True):
        repeat = 0
        while repeat < self.retry:
            repeat += 1
            try:
                msg = self._packet(cmd)
                self.sock.sendto(msg, (self.host, self.port))
                if not receive:
                    return
                data, address = self.sock.recvfrom(300)
                self.logger.debug("< %s", data.hex())
                size = len(data)
                if size > 42:
                    pkt_id = unpack_from("H", data, offset=40)[0]
                    error = unpack_from("I", data, offset=36)[0]
                    pkt_id &= 0x7FFF
                    if (pkt_id != self.pkt_id) or (error != 0):
                        self.logger.debug("Req/Rsp: Packet ID %X/%X, Error %d" % (self.pkt_id, pkt_id, error))
                        raise smaError("Inverter answer does not match our parameters.")
                else:
                    raise smaError("Format of inverter response does not fit.")
                return data
            except TimeoutError as e:
                self.logger.error("Timeout")
                continue

            raise smaError("No response")

    def _login(self):
        data = self._send_recieve("login")
        if data:
            inv_susyid, inv_serial = unpack_from("<HI", data, offset=28)
            self.serial = inv_serial
            self.target_id = inv_susyid.to_bytes(2, byteorder='little') + inv_serial.to_bytes(4, byteorder='little')
            self.logger.debug("Logged in to inverter susyid: %d, serial: %d" % (inv_susyid, inv_serial))
            return True
        return False

    def _logout(self):
        self._send_recieve("logout", False)
        self.pkt_id = 0
        return True

    def _fetch(self, command):
        data = self._send_recieve(command)
        data_len = len(data)
        if data:
            cmd = unpack_from("H", data, offset=55)[0]
            self.logger.debug("Data identifier %02X" % cmd)
            if cmd == 0x821E:
                inv_class = unpack_from("I", data, offset=102)[0] & 0x00FFFFFF
                i = 142
                inv_type = 0
                while (unpack_from("I", data, offset=i)[0] != 0x00FFFFFE) and i < data_len: # 0x00FFFFFE is the end marker for attributes
                    temp = unpack_from("I", data, offset=i)[0]
                    if (temp & 0xFF000000) == 0x01000000: # in some models a catalogue is transmitted, right model marked with: 0x01000000 OR INV_Type
                        inv_type = temp & 0x00FFFFFF
                    i = i + 4
                self.inv_class = str(inv_class)
                self.inv_type = str(inv_type)
                if inv_class in SMA_INV_CLASS:
                    self.inv_class = SMA_INV_CLASS[inv_class]
                if inv_type in SMA_INV_TYPE:
                    self.inv_type = SMA_INV_TYPE[inv_type]
                    
            elif cmd == 0x2601:
                if data_len >= 66:
                    value = unpack_from("I", data, offset=62)[0]
                    if (value != 0x80000000) and (value != 0xFFFFFFFF) and (value > 0):
                        self.sensors['energy_total']['value'] = value / 1000
                if data_len >= 82:
                    value = unpack_from("I", data, offset=78)[0]
                    self.sensors['energy_today']['value'] = value / 1000

            elif cmd == 0x263F:
                value = unpack_from("I", data, offset=62)[0]
                if (value == 0x80000000):
                    value = 0
                self.sensors['power_ac_total']['value'] = value
            return

    def init(self):
        self._login()
        self._fetch("info")
        self._logout()
    
    def update(self):
        self._login()
        self._fetch("energy")
        self._fetch("power_ac_total")
        self._logout()
