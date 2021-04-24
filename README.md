# AithreToHud

## Introduction

This is a service that communicates with devices in the Aithre product range. The service maintains connections to those devices, reads their status, then makes available the data.

## Intended Usage

The primary purpose is for this service to be used by the StratuxHud project.

## Parts List

This service currently works with the following devices:

- Aithre Carbon Monoxide Detector
- Illyrian Blood Pulse Oxygen Meter.

## Installation

This service is included in the StratuxHud image.

If you are using the default release image, then no additional work is required.

These installation steps are intended for developers or those who wish to install from scratch.

```bash
pushd /usr/local/lib/python3.7/dist-packages/bluepy-1.3.0-py3.7.egg/bluepy
sudo make
sudo setcap cap_net_raw+e  bluepy-helper
sudo setcap cap_net_admin+eip  bluepy-helper
```

### Notes

- For some installations, PIP3 does not appear to compile bluepy-helper, hence the `make` step.
- The exact path that `make` needs to be run in may differ.
- The `setcap` steps allow BlueTooth to be used while **NOT** running as the `root` user.

### Revision History

Date       | Version   | Major Changes
---------- | --------- | --------------------------------------------
2020-04-24 | 1.0 Alpha | Initial port to Python 3, moved to own Repo.
