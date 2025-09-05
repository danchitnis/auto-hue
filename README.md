# auto-hue
Python automation for Phliphs Hue light bulbs

## config

in `appdaemon.yaml` do:

```yaml
kitchen_light_cycle:
  module: kitchen_light_cycle
  class: KitchenLightCycle
```

## finding device ID

There are a few methods to find the device ID:

### using URL of the device

1. go to homeassistant settings
2. navigate to the devices section
3. find your Philips Hue device in the list
4. click on the device to open its settings
5. look for the "Device ID" or "Unique ID" in the URL of the browser
