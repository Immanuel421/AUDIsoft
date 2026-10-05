# ADC-Test für Bodenfeuchte

Diese Datei prueft nur die Anschlusserkennung. Sie veraendert weder
`config.json` noch SD-Daten und startet keine normale Messung.

1. Originale `code.py` auf dem betreffenden Pico sichern.
2. `tests/soil_moisture_adc_test.py` als `code.py` nach CIRCUITPY kopieren.
3. Pico sicher auswerfen oder die Dateiuebertragung abwarten. Der Test startet
   automatisch und gibt jede Sekunde Werte fuer GP26, GP27 und GP28 aus.
4. Sensor in Luft halten und Werte notieren. Dann in feuchte Erde oder Wasser
   halten und dieselben Werte vergleichen.
5. Der Eingang mit einer deutlichen, wiederholbaren Veraenderung ist der am
   Sensor gelbe Signaldraht angeschlossene ADC-Pin.
6. Die originale `code.py` wiederherstellen und den Pico neu starten.

Vor dem Test muss der Sensor nach Auskunft von Herrn Schnabel korrekt
angeschlossen sein: Rot an `+3.3V`, Gelb an `ADC` und ein schwarzer Leiter an
`GND`. Der zweite schwarze Leiter dient als Abschirmung und bleibt frei. Der
Test liest nur; er kalibriert noch keine Bodenfeuchte in Prozent und schreibt
keine CSV-Zeile.

## Hardwarebefund vom 21.09.2026

- Der Sensor ist ein DFRobot Waterproof Capacitive Soil Moisture Sensor V2.0.
- Laut Herrn Schnabel liegt der ADC-Anschluss der Tragerplatine auf `GP27`.
  Dieser Pin wird auch vom optionalen DS18B20 verwendet; beide Bodensensoren
  koennen daher nicht gleichzeitig betrieben werden.
- Bei wiederholten Vergleichsmessungen in Luft und Wasser lagen die Werte auf
  `GP27` nur bei etwa 0 bis 0,02 V. Ein reproduzierbares Sensorsignal wurde
  damit noch nicht nachgewiesen.
- Der Befund belegt keinen Sensor- oder Platinenfehler. Signalweg und
  Versorgung muessen bei einem weiteren Hardwaretermin gezielt geprueft
  werden.
