"""JSON-Konfiguration fuer die rollenabhaengige Composition Root."""

import json

from domain.plausibility import validate_limits
from ports.errors import ConfigurationError

DEFAULT_RADIO = {
    "frequency_mhz": 868.1,
    "bandwidth_khz": 125.0,
    "spreading_factor": 7,
    "coding_rate": 5,
    "tx_power_dbm": 10,
    "sync_word": 18,
}


def _validate_device_id(device_id, field_name):
    if not isinstance(device_id, str) or not 1 <= len(device_id) <= 8:
        raise ConfigurationError(
            "{} must contain 1..8 characters".format(field_name)
        )
    for character in device_id:
        valid = character.isdigit() or "A" <= character <= "Z"
        if not valid and character not in "_-":
            raise ConfigurationError("{} contains invalid characters".format(field_name))


def _validate_network_configuration(config):
    network_mode = config.get("network_mode", "star")
    if network_mode not in ("star", "mesh"):
        raise ConfigurationError("network_mode must be star or mesh")
    config["network_mode"] = network_mode

    if network_mode != "mesh":
        return

    device_id = config["device_id"]
    if config["role"] == "slave":
        next_hop_id = config.get("next_hop_id")
        _validate_device_id(next_hop_id, "next_hop_id")
        if next_hop_id == device_id:
            raise ConfigurationError("slave next_hop_id must differ from device_id")
        hop_limit = config.get("hop_limit")
        if isinstance(hop_limit, bool) or not isinstance(hop_limit, int) or hop_limit < 1:
            raise ConfigurationError("mesh hop_limit must be a positive integer")

    reverse_hops = config.get("return_next_hops", {})
    if not isinstance(reverse_hops, dict):
        raise ConfigurationError("return_next_hops must be an object")
    for origin_id, next_hop_id in reverse_hops.items():
        _validate_device_id(origin_id, "return_next_hops origin")
        _validate_device_id(next_hop_id, "return_next_hops next hop")
        if next_hop_id == device_id:
            raise ConfigurationError("return route must not point to itself")


def _validate_role_configuration(config):
    role = config["role"]
    device_id = config["device_id"]
    if role == "slave":
        master_id = config.get("master_id")
        _validate_device_id(master_id, "master_id")
        if master_id == device_id:
            raise ConfigurationError("slave master_id must differ from device_id")
        return

    monitored = config.get("monitored_slaves")
    if not isinstance(monitored, list) or len(monitored) < 1:
        raise ConfigurationError(
            "master monitored_slaves must contain at least one device ID"
        )
    if len(set(monitored)) != len(monitored):
        raise ConfigurationError("monitored_slaves must not contain duplicates")
    for slave_id in monitored:
        _validate_device_id(slave_id, "monitored_slaves entry")
        if slave_id == device_id:
            raise ConfigurationError(
                "master device_id must not be monitored as a slave"
            )


def load_configuration(path="/config.json"):
    try:
        with open(path, "r") as config_file:
            config = json.load(config_file)
    except (OSError, ValueError) as exc:
        raise ConfigurationError(
            "configuration cannot be loaded from {}: {}".format(path, exc)
        )

    role = config.get("role")
    if role not in ("master", "slave"):
        raise ConfigurationError("role must be master or slave")
    if not config.get("device_id"):
        raise ConfigurationError("device_id is required")
    _validate_device_id(config["device_id"], "device_id")
    _validate_network_configuration(config)
    _validate_role_configuration(config)

    config.setdefault("measurement_interval_s", 900)
    soil_moisture = config.get("soil_moisture")
    if soil_moisture is not None:
        if not isinstance(soil_moisture, dict):
            raise ConfigurationError("soil_moisture must be an object")
        enabled = soil_moisture.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ConfigurationError("soil_moisture enabled must be boolean")
        if not enabled:
            config["soil_moisture"] = None
            soil_moisture = None
    if soil_moisture is not None:
        for name in ("dry_raw", "wet_raw"):
            value = soil_moisture.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 65535:
                raise ConfigurationError("soil_moisture {} must be 0..65535".format(name))
        if soil_moisture["dry_raw"] == soil_moisture["wet_raw"]:
            raise ConfigurationError("soil_moisture calibration values must differ")
    try:
        config["plausibility_limits"] = validate_limits(
            config.get("plausibility_limits", {})
        )
    except ValueError as exc:
        raise ConfigurationError(str(exc))
    config.setdefault("ack_timeout_ms", 3000)
    config.setdefault("receive_timeout_ms", 30000)
    radio = config.setdefault("radio", {})
    for key, value in DEFAULT_RADIO.items():
        radio.setdefault(key, value)
    return config
