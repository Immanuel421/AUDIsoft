"""Einbindung der SD-Karte ueber den vorhandenen SPI-Anschluss."""

import gc

import board
import busio
import sdcardio
import storage

from ports.errors import StorageError


class SdCardAdapter:
    def __init__(self, mount_path="/sd"):
        self.mount_path = mount_path
        self.spi = None
        self.card = None

    def mount(self):
        try:
            self.spi = busio.SPI(
                clock=board.GP18, MOSI=board.GP19, MISO=board.GP16
            )
            self.card = sdcardio.SDCard(self.spi, board.GP17)
            # VfsFat needs a contiguous 4 KiB buffer on the RP2350.
            # Free setup temporaries immediately before that allocation.
            gc.collect()
            vfs = storage.VfsFat(self.card)
            storage.mount(vfs, self.mount_path)
        except Exception as exc:
            raise StorageError(
                "SD card cannot be mounted at {}: {}".format(
                    self.mount_path, exc
                )
            )
        return self.mount_path
