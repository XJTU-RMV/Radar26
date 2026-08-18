from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass


DEFAULT_SIGNAL_SERIAL = "03df62c27fcb392820d76aca77d3213038"
DEFAULT_JAMMING_SERIAL = "03d760669013192125df686e980b01393d"


@dataclass(frozen=True)
class PlutoDevice:
    serial: str
    uri: str


def list_usb_plutos() -> list[PlutoDevice]:
    out = subprocess.check_output(["iio_info", "-s"], text=True, errors="ignore")
    devices = []
    for line in out.splitlines():
        serial = re.search(r"serial=([0-9a-fA-F]+)", line)
        uri = re.search(r"\[(usb:[^\]]+)\]", line)
        if serial and uri:
            devices.append(PlutoDevice(serial.group(1), uri.group(1)))
    return devices


def usb_uri_for_serial(serial: str) -> str:
    matches = [device.uri for device in list_usb_plutos() if device.serial == serial]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one USB PlutoSDR with serial {serial}, found {len(matches)}")
    return matches[0]
