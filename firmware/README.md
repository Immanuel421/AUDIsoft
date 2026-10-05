# Firmware-Pakete

Die Ordner enthalten vorkompilierte Projektmodule fuer CircuitPython. Sie
werden aus dem aktuellen Quellcode mit `build/build_firmware.py` erzeugt.

| Paket | Zielgeraete | CircuitPython |
|---|---|---|
| `rp2040/` | C02, C03 | 10.3.0 |
| `rp2350/` | C01, M01 | 10.2.1 |

Die Pakete sind nicht austauschbar. Eine `.mpy`-Datei darf nur auf einem
Geraet mit der zugehoerigen CircuitPython-Version eingesetzt werden.

`code.py` bleibt als Python-Datei erhalten, weil CircuitPython diese Datei beim
Start direkt ausfuehrt. Die vier Projektpakete werden als `.mpy` ausgeliefert,
um beim Import RAM zu sparen.

## Paket Neu Erzeugen

Nach jeder Aenderung an `code.py`, `adapters/`, `application/`, `domain/` oder
`ports/` beide Pakete mit dem jeweils passenden `mpy-cross` neu bauen:

```sh
python3 build/build_firmware.py rp2040 --mpy-cross /pfad/zu/mpy-cross-10.3.0
python3 build/build_firmware.py rp2350 --mpy-cross /pfad/zu/mpy-cross-10.2.1
```

Die erzeugte `sources.json` dokumentiert den exakten Quellstand. Vor der
Installation stets die jeweilige `INSTALLATION.md` lesen und den Inhalt des
Picos sichern.
