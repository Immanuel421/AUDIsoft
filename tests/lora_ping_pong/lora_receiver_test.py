"""Isolierter LoRa-Pong-Test fuer Pico + Waveshare SX1262 unter CircuitPython."""

import board
from sx1262 import SX1262

# Muss mit der Konfiguration des Senders uebereinstimmen.
FREQUENCY_MHZ = 868.1
BANDWIDTH_KHZ = 125.0
SPREADING_FACTOR = 7
CODING_RATE = 5
TX_POWER_DBM = 10
RECEIVE_TIMEOUT_MS = 30000


def status_text(status):
    return SX1262.STATUS.get(status, str(status))


def create_radio():
    radio = SX1262(
        spi_bus=1,
        clk=board.GP10,
        mosi=board.GP11,
        miso=board.GP12,
        cs=board.GP3,
        irq=board.GP20,
        rst=board.GP15,
        gpio=board.GP2,
    )
    status = radio.begin(
        freq=FREQUENCY_MHZ,
        bw=BANDWIDTH_KHZ,
        sf=SPREADING_FACTOR,
        cr=CODING_RATE,
        syncWord=0x12,
        power=TX_POWER_DBM,
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
    print("LoRa init:", status_text(status))
    return radio


radio = create_radio()
print("Warte auf PING ...")

while True:
    payload, receive_status = radio.recv(
        timeout_en=True,
        timeout_ms=RECEIVE_TIMEOUT_MS,
    )
    if not payload:
        print("Kein Paket:", status_text(receive_status))
        continue

    print(
        "Empfangen:",
        payload,
        status_text(receive_status),
        "RSSI:",
        radio.getRSSI(),
        "SNR:",
        radio.getSNR(),
    )

    if payload.startswith(b"PING:"):
        response = b"PONG:" + payload[5:]
        sent_length, send_status = radio.send(response)
        print("Gesendet:", response, sent_length, status_text(send_status))
    else:
        print("Ignoriert: kein PING-Paket")
