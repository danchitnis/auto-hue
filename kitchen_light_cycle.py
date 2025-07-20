import appdaemon.plugins.hass.hassapi as hass

class KitchenLightCycle(hass.Hass):
    # your sequences
    lights_map = {
        0: ["light.hue_ambiance_spot_5"],
        1: ["light.hue_ambiance_spot_10", "light.hue_ambiance_spot_7"],
        2: ["light.hue_ambiance_spot_4", "light.hue_ambiance_spot_3"],
        3: ["light.hue_ambiance_spot_1", "light.hue_ambiance_spot_2", "light.hue_ambiance_spot_6"]
    }

    def initialize(self):
        self.log("KitchenLightCycle app initialized!")
        # -1 = all off
        self.idx = -1
        device = "{id of your hue switch}"

        # +, –, power
        self.listen_event(self.button_plus,  "hue_event", device_id=device, subtype=2, type="initial_press")
        self.listen_event(self.button_minus, "hue_event", device_id=device, subtype=3, type="initial_press")
        self.listen_event(self.button_power, "hue_event", device_id=device, subtype=1, type="initial_press")

    def button_plus(self, event_name, data, kwargs):
        prev = self.idx
        # advance: -1→0→1→2→3→-1…
        if self.idx < 0:
            self.idx = 0
        elif self.idx < len(self.lights_map) - 1:
            self.idx += 1
        else:
            self.idx = -1
        self.log(f"➕ from {prev} to {self.idx}")

        # if we're now on a valid group, turn it on
        if self.idx >= 0:
            for light in self.lights_map[self.idx]:
                self.call_service("light/turn_on",
                                  entity_id=light,
                                  brightness_pct=60,
                                  transition=2)

    def button_minus(self, event_name, data, kwargs):
        prev = self.idx
        # if in a group, turn it off first
        if self.idx >= 0:
            for light in self.lights_map[self.idx]:
                self.call_service("light/turn_off",
                                  entity_id=light,
                                  transition=2)
        # step back: 3→2→1→0→-1 and stay at -1
        if self.idx > 0:
            self.idx -= 1
        else:
            self.idx = -1
        self.log(f"➖ from {prev} to {self.idx}")

    def button_power(self, event_name, data, kwargs):
        prev = self.idx
        all_lights = [l for grp in self.lights_map.values() for l in grp]

        if self.idx < 0:
            # off → all on, jump to last
            for light in all_lights:
                self.call_service("light/turn_on",
                                  entity_id=light,
                                  brightness_pct=60,
                                  transition=2)
            self.idx = len(self.lights_map) - 1
        else:
            # any on → all off, reset to -1
            for light in all_lights:
                self.call_service("light/turn_off",
                                  entity_id=light,
                                  transition=2)
            self.idx = -1

        self.log(f"⏻ from {prev} to {self.idx}")
