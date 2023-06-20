# datalogger-gui
datalogger-gui is used to monitor different kind of devices with a common interface.

## key points:
- minimal driver for specific instrument -> simpler to add a new device
- common file management/communications for all instruments
- testDevice for offline dev
- abstracted instrument management

## TODO/ideas
- config file
	- save current config
	- load saved config
- CLI mode based on saved config
- be able to log different devices and save values on one file
