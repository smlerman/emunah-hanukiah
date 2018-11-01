# emunah-hanukiah
Raspberry Pi software for controlling an electric hanukiah

## Wii Remote Controls

The package includes a service that listens for Bluetooth connections from a Wii Remote. In order to pair a Wii Remote, press the `1` and `2` buttons at the same time.

* Swing or `A` button: Turn on the next light according to the current date. This turns on lights in the traditional order, starting with 0 and then going left to right. If all of the lights that should be on for the current day are on, turn off all of the lights.
* `B` button: Turn on the next light, i.e. the right-most light that is off. If all of the lights are on, turn all of the lights off.
* Directional Pad `Left`: Change the current light to be controlled by the Up/Down buttons one light to the left. If the current light is 8, change to 0.
* Directional Pad `Right`: Change the current light to be controlled by the Up/Down buttons one light to the right. If the current light is 0, change to 8.
* Directional Pad `Up`: Turn on the current light
* Directional Pad `Down`: Turn off the current light


## Keyboard Shortcuts

There are keyboard shortcuts `Ctrl-Alt-0` through `Ctrl-Alt-8` to toggle each individual light.
