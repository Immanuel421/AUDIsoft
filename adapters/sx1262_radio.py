"""SX1262-Adapter mit der am 11.08.2026 getesteten Pinbelegung."""

import time

import board
from _sx126x import (
    ERR_RX_TIMEOUT, SX126X_IRQ_RX_DONE, SX126X_IRQ_CRC_ERR,
    SX126X_IRQ_HEADER_ERR,
)
from sx1262 import SX1262

from ports.contracts import RadioPort
from ports.errors import RadioError


class Sx1262RadioAdapter(RadioPort):
    def __init__(self, config):
        try:
            self._radio = SX1262(
                spi_bus=1,
                clk=board.GP10,
                mosi=board.GP11,
                miso=board.GP12,
                cs=board.GP3,
                irq=board.GP20,
                rst=board.GP15,
                gpio=board.GP2,
            )
            status = self._radio.begin(
                freq=config["frequency_mhz"],
                bw=config["bandwidth_khz"],
                sf=config["spreading_factor"],
                cr=config["coding_rate"],
                syncWord=config["sync_word"],
                power=config["tx_power_dbm"],
                currentLimit=60.0,
                preambleLength=8,
                implicit=False,
                implicitLen=0xFF,
                crcOn=True,
                txIq=False,
                rxIq=False,
                tcxoVoltage=1.7,
                useRegulatorLDO=False,
                blocking=True,
            )
        except Exception as exc:
            raise RadioError("LoRa initialization failed: {}".format(exc))
        if status != 0:
            raise RadioError("LoRa initialization failed: {}".format(status))
        self._start_receive()

    def _start_receive(self):
        # Single-packet RX keeps an early reply buffered until receive reads it.
        status = self._radio.startReceive(0)
        if status != 0:
            raise RadioError("LoRa receive setup failed: {}".format(status))

    def send(self, payload):
        try:
            # Allow the previous sender and overhearing relays to re-arm RX.
            time.sleep(0.05)
            sent_length, status = self._radio.send(payload)
            self._start_receive()
        except Exception as exc:
            raise RadioError("LoRa send failed: {}".format(exc))
        return status == 0 and sent_length == len(payload)

    def receive(self, timeout_ms):
        try:
            deadline = time.monotonic() + max(0, timeout_ms) / 1000
            while True:
                irq = self._radio.getIrqStatus()
                if irq & (SX126X_IRQ_CRC_ERR | SX126X_IRQ_HEADER_ERR):
                    self._radio.standby()
                    self._start_receive()
                elif irq & SX126X_IRQ_RX_DONE:
                    payload = bytearray(self._radio.getPacketLength())
                    status = self._radio.readData(payload, len(payload))
                    metadata = {
                        "status": status,
                        "rssi_dbm": self._radio.getRSSI(),
                        "snr_db": self._radio.getSNR(),
                    }
                    self._start_receive()
                    if status == 0 and payload:
                        return bytes(payload), metadata
                if time.monotonic() >= deadline:
                    # A software timeout must not interrupt an incoming packet.
                    return None, {"status": ERR_RX_TIMEOUT}
                time.sleep(0.001)
        except Exception as exc:
            raise RadioError("LoRa receive failed: {}".format(exc))
