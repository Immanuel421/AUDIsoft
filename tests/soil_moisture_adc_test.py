"""Temporärer Hardwaretest für den kapazitiven Bodenfeuchtesensor.

Diese Datei voruebergehend als /code.py auf CIRCUITPY verwenden. Sie startet
weder SEN66, SD, LoRa noch die normale 15-Minuten-Messung.
"""

import analogio
import board
import time

DRY = 42000
WET = 2800
CHANNELS = (
    ("GP27 / ADC1", board.GP27),
    ("GP26 / ADC0", board.GP26),
    ("GP28 / ADC2", board.GP28),
)

def read_soil(raw_value):
    percent = (DRY - raw_value) * 100 / (DRY - WET)

    if percent < 0:
        percent = 0

    if percent > 100:
        percent = 100

    return round(percent)


def voltage(raw_value):
    return raw_value * 3.3 / 65535


def build_display():
    try:
        from adapters.oled_display import OledDisplayAdapter
        display = OledDisplayAdapter()
        display.show_message("Soil ADC", ["Test startet ..."])
        return display
    except Exception as exc:
        print("OLED unavailable:", exc)
        return None


def main():
    inputs = []
    for name, pin in CHANNELS:
        try:
            inputs.append((name, analogio.AnalogIn(pin)))
            print("ADC ready:", name)
        except Exception as exc:
            print("ADC unavailable:", name, exc)

    print("Soil-moisture ADC test started")
    print("Compare values in air and in wet soil or water.")
    display = build_display()
    while True:
        lines = []
        for name, channel in inputs:
            raw_value = channel.value
            message = "{}: raw={} voltage={:.3f}V".format(
                name, raw_value, voltage(raw_value)
            )
            if name == "GP27 / ADC1":
                soil_percent = read_soil(raw_value)
                print("ADC1: raw={} voltage={:.3f}V moisture={}%".format(
                    raw_value, voltage(raw_value), soil_percent
                ))
                lines.append("ADC1 raw: {}".format(raw_value))
                lines.append("ADC1: {}%".format(soil_percent))
            else:
                print(message)
                lines.append("{}: {}".format(name[2:4], raw_value))
        if display is not None:
            display.show_message("Soil ADC", lines)
        time.sleep(1)


main()
