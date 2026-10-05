"""Isolierter LoRa-Ping-Test fuer Pico + Waveshare SX1262 unter CircuitPython."""

import time

import board
from sx1262 import SX1262

# Vorlaeufige Testwerte. Vor dem Feldeinsatz regulatorisch und fachlich pruefen.
FREQUENCY_MHZ = 868.1
BANDWIDTH_KHZ = 125.0
SPREADING_FACTOR = 7
CODING_RATE = 5
TX_POWER_DBM = 10
PING_INTERVAL_S = 10
RESPONSE_TIMEOUT_MS = 3000


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
sequence = 0

while True:
    payload = "PING:{:04d}".format(sequence).encode("ascii")
    sent_length, send_status = radio.send(payload)
    print("Gesendet:", payload, sent_length, status_text(send_status))

    response, receive_status = radio.recv(
        timeout_en=True,
        timeout_ms=RESPONSE_TIMEOUT_MS,
    )
    if response:
        print(
            "Empfangen:",
            response,
            status_text(receive_status),
            "RSSI:",
            radio.getRSSI(),
            "SNR:",
            radio.getSNR(),
        )
    else:
        print("Keine Antwort:", status_text(receive_status))

    sequence = (sequence + 1) % 10000
    time.sleep(PING_INTERVAL_S)
