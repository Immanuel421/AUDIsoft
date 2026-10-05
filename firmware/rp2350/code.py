"""Composition Root fuer Master- und Slave-Climate-Cubes."""

import gc
import time

from ports.errors import ClimateCubeError

STARTUP_STAGE = "initializing"


def set_startup_stage(stage):
    global STARTUP_STAGE
    STARTUP_STAGE = stage
    print("startup:", stage)



def report_failure(diagnostics, context, exc):
    gc.collect()
    import sys
    if hasattr(sys, "print_exception"):
        sys.print_exception(exc)
    if isinstance(exc, ClimateCubeError):
        diagnostics.error("{}: {}".format(context, exc))
    else:
        diagnostics.error(
            "unexpected {} ({}): {}".format(
                context, type(exc).__name__, exc
            )
        )


def build_diagnostics():
    from adapters.diagnostics import DiagnosticsAdapter

    # The SD driver needs a contiguous heap allocation. Keep the display
    # uninitialized until the storage mount has completed.
    return DiagnosticsAdapter(), None


def attach_oled(diagnostics):
    oled = None
    try:
        set_startup_stage("OLED driver")
        from adapters.oled_display import OledDisplayAdapter

        oled = OledDisplayAdapter()
        oled.show_startup()
    except Exception as exc:
        print("ERROR: OLED initialization failed:", exc)
        return None

    diagnostics.set_oled(oled)
    return oled


def build_shared_components(config, diagnostics):
    set_startup_stage("clock adapter")
    from adapters.clock import ConfiguredUtcClock
    set_startup_stage("SD adapter")
    from adapters.sd_card import SdCardAdapter
    from ports.errors import StorageError, StorageMigrationError

    gc.collect()
    sd_card = None
    storage = None
    try:
        set_startup_stage("SD initialization")
        diagnostics.info("mounting SD card")
        sd_card = SdCardAdapter()
        mount_path = sd_card.mount()
        gc.collect()
        set_startup_stage("storage adapter")
        from adapters.sd_storage import SdStorageAdapter

        # Existing archives are not scanned on every boot. The durable state
        # file is sufficient for normal operation and avoids a corrupt old
        # archive delaying a deployed device.
        storage = SdStorageAdapter(mount_path, scan_existing_data=False)
        diagnostics.info("SD card ready")
    except StorageError as exc:
        if config["role"] != "slave" or isinstance(exc, StorageMigrationError):
            raise
        diagnostics.error(
            "slave SD unavailable; starting degraded mode: {}".format(exc)
        )

    set_startup_stage("clock initialization")
    last_timestamp = None
    if storage is not None:
        try:
            last_timestamp = storage.latest_measurement_timestamp(
                config["device_id"]
            )
        except StorageError as exc:
            diagnostics.error(
                "previous timestamp unavailable; using configured time: {}".format(
                    exc
                )
            )
    clock = ConfiguredUtcClock(
        config.get("time_epoch_utc"), last_timestamp,
        config["measurement_interval_s"],
    )
    if clock.status_flags():
        diagnostics.info("continuing time from previous measurement")

    gc.collect()
    set_startup_stage("LoRa adapter")
    from adapters.sx1262_radio import Sx1262RadioAdapter

    set_startup_stage("LoRa initialization")
    diagnostics.info("initializing LoRa")
    radio = Sx1262RadioAdapter(config["radio"])
    diagnostics.info("LoRa ready")
    return sd_card, storage, clock, radio


def build_sensor(config, diagnostics, oled):
    set_startup_stage("sensor adapters")
    from adapters.ds18b20_sensor import Ds18b20SensorAdapter
    from adapters.sen66_sensor import Sen66SensorAdapter
    soil_moisture_config = config.get("soil_moisture")

    if oled is not None:
        i2c = oled.i2c
    else:
        import board
        import busio

        i2c = busio.I2C(
            scl=board.GP1, sda=board.GP0, frequency=100000
        )

    soil_sensor = None
    soil_moisture_sensor = None
    if soil_moisture_config is not None:
        from adapters.soil_moisture_sensor import SoilMoistureSensorAdapter
        try:
            soil_moisture_sensor = SoilMoistureSensorAdapter(
                soil_moisture_config["dry_raw"], soil_moisture_config["wet_raw"]
            )
            diagnostics.info("soil moisture sensor initialized")
        except Exception as exc:
            diagnostics.info("soil moisture unavailable: {}".format(exc))
    else:
        try:
            soil_sensor = Ds18b20SensorAdapter()
            diagnostics.info("DS18B20 initialized")
        except Exception as exc:
            diagnostics.info("DS18B20 unavailable: {}".format(exc))

    diagnostics.info("initializing SEN66")
    sensor = Sen66SensorAdapter(
        i2c,
        warmup_s=int(config.get("sen66_warmup_s", 60)),
        soil_sensor=soil_sensor,
        soil_moisture_sensor=soil_moisture_sensor,
    )
    diagnostics.info("SEN66 initialized")
    return sensor


def build_slave(config, diagnostics, oled, storage, clock, radio):
    sensor = build_sensor(config, diagnostics, oled)
    set_startup_stage("slave controller")
    from application.slave_controller import SlaveController
    from domain.protocol import AsciiProtocolCodec

    return SlaveController(
        config["device_id"],
        sensor,
        clock,
        storage,
        radio,
        AsciiProtocolCodec(),
        diagnostics,
        int(config["ack_timeout_ms"]),
        master_id=config.get("master_id"),
        next_hop_id=config.get("next_hop_id", config.get("master_id")),
        hop_limit=int(config.get("hop_limit", 1)),
        plausibility_limits=config["plausibility_limits"],
    )


def build_master(config, diagnostics, storage, clock, radio, oled=None):
    sensor = build_sensor(config, diagnostics, oled)
    set_startup_stage("master controller")
    from application.master_controller import MasterController
    from domain.protocol import AsciiProtocolCodec

    return MasterController(
        config["device_id"],
        clock,
        storage,
        radio,
        AsciiProtocolCodec(),
        diagnostics,
        monitored_slaves=config["monitored_slaves"],
        return_next_hops=config.get("return_next_hops"),
        sensor=sensor,
        measurement_interval_s=config["measurement_interval_s"],
        plausibility_limits=config["plausibility_limits"],
    )


def run_slave(controller, config, diagnostics, relay=None):
    interval_s = int(config["measurement_interval_s"])
    sequence_retry_s = int(config.get("sequence_query_retry_s", 60))
    next_measurement_at = 0
    diagnostics.info("slave {} started".format(config["device_id"]))
    try:
        controller.report_device_restarted()
    except Exception as exc:
        report_failure(diagnostics, "device restart event failed", exc)
    while True:
        cycle_started = time.monotonic()
        try:
            if controller.storage is None:
                refresh_measurement = cycle_started >= next_measurement_at
                controller.run_measurement_cycle_without_local_storage(
                    refresh_measurement
                )
                if refresh_measurement:
                    next_measurement_at = cycle_started + interval_s
            else:
                controller.run_measurement_cycle()
                next_measurement_at = cycle_started + interval_s
        except Exception as exc:
            report_failure(diagnostics, "measurement cycle failed", exc)
        remaining = next_measurement_at - time.monotonic()
        if (controller.storage is None
                and controller.volatile_held_measurement is not None
                and controller.volatile_next_sequence is None):
            remaining = min(remaining, sequence_retry_s)
        while remaining > 0:
            if relay is None:
                time.sleep(remaining)
                break
            relay.process_next(
                min(int(remaining * 1000), int(config["receive_timeout_ms"]))
            )
            remaining = next_measurement_at - time.monotonic()


def run_master(controller, config, diagnostics):
    timeout_ms = min(100, int(config["receive_timeout_ms"]))
    diagnostics.info("master {} started".format(config["device_id"]))
    while True:
        try:
            controller.poll_missing_intervals()
        except Exception as exc:
            report_failure(diagnostics, "master interval monitoring failed", exc)
        try:
            controller.poll_measurement()
        except Exception as exc:
            report_failure(diagnostics, "master measurement cycle failed", exc)
        try:
            controller.process_next(timeout_ms)
        except Exception as exc:
            report_failure(diagnostics, "master receive cycle failed", exc)


def start_configured_role(
        config, diagnostics, oled, storage, clock, radio):
    if config["role"] == "slave":
        controller = build_slave(
            config, diagnostics, oled, storage, clock, radio
        )
        relay = None
        if config["network_mode"] == "mesh":
            diagnostics.info("loading relay components")
            gc.collect()
            set_startup_stage("relay storage import")
            from adapters.relay_storage import RelayStorageAdapter
            diagnostics.info("relay storage component loaded")
            gc.collect()
            set_startup_stage("relay controller import")
            from application.relay_controller import RelayController
            diagnostics.info("relay controller component loaded")

            diagnostics.info("initializing relay storage")
            relay_storage = RelayStorageAdapter()
            diagnostics.info("relay storage ready")
            relay = RelayController(
                config["device_id"], config["master_id"],
                config["next_hop_id"], config.get("return_next_hops"),
                radio, controller.codec, diagnostics, config["ack_timeout_ms"],
                relay_storage,
            )
        if relay is not None:
            diagnostics.info("retrying relay queue")
            relay.retry_pending()
        diagnostics.info("starting slave loop")
        run_slave(controller, config, diagnostics, relay)
    else:
        controller = build_master(
            config, diagnostics, storage, clock, radio, oled
        )
        run_master(controller, config, diagnostics)


def main():
    print("AUDI Climate Cube")
    print("Hochschule Hof / AUDI Umweltstiftung")
    print("Starte System ...")

    diagnostics, oled = build_diagnostics()
    try:
        set_startup_stage("configuration")
        from adapters.configuration import load_configuration

        diagnostics.info("loading configuration")
        config = load_configuration()
        _sd_card, storage, clock, radio = build_shared_components(
            config, diagnostics
        )
        oled = attach_oled(diagnostics)
        start_configured_role(
            config, diagnostics, oled, storage, clock, radio
        )
    except Exception as exc:
        failure_stage = STARTUP_STAGE
        if oled is None:
            attach_oled(diagnostics)
        report_failure(
            diagnostics, "startup failed at " + failure_stage, exc
        )
        while True:
            time.sleep(30)


main()
