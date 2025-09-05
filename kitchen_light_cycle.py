import appdaemon.plugins.hass.hassapi as hass


class KitchenLightCycle(hass.Hass):

    #
    # 1️⃣  Alias → entity_id look-up table
    #     (edit this once; use the short names everywhere else)
    #     find this in Developer Tools → States
    #
    alias_map = {
        "A1": "light.hue_ambiance_spot_10",
        "A2": "light.hue_ambiance_spot_5",
        "A3": "light.hue_ambiance_spot_7",
        "B1": "light.hue_ambiance_spot_4",
        "B2": "light.hue_ambiance_spot_6",
        "B3": "light.hue_ambiance_spot_3",
        "C1": "light.hue_ambiance_spot_1",
        "C2": "light.hue_ambiance_spot_2",
        "D1": "light.hue_ambiance_spot_8",
        "D2": "light.hue_ambiance_spot_9",

    }

    #
    # 2️⃣  Your cycle, expressed only with the aliases above
    #
    sequences = [
        ["A2"],                       # idx 0
        ["A1", "A3"],                 # idx 1
        ["B1", "B3"],                 # idx 2
        ["C1", "C2"],                 # idx 3
        ["D1", "D2", "B2"],           # idx 4
    ]
    # (keep as many steps as you like – the rest of the code adapts)

    # ------------------------------------------------------------------ #
    # nothing below here normally needs editing
    # ------------------------------------------------------------------ #

    def initialize(self):
        self.log("KitchenLightCycle app initialised")

        device = "your_switch_id"     # Hue switch

        self.idx = -1          # -1 means “all lights off”

        self.listen_event(self.button_plus,  "hue_event",
                          device_id=device, subtype=2, type="initial_press")
        self.listen_event(self.button_minus, "hue_event",
                          device_id=device, subtype=3, type="initial_press")
        self.listen_event(self.button_power, "hue_event",
                          device_id=device, subtype=1, type="initial_press")

    # ---------- helpers ------------------------------------------------

    def _expand(self, alias_list):
        """Translate ['A2', 'A3'] → ['light.hue_ambiance_spot_5', …]."""
        return [self.alias_map[a] for a in alias_list]

    @property
    def _all_entity_ids(self):
        """Flat list of every light that appears in any sequence."""
        return [self.alias_map[a]
                for seq in self.sequences for a in seq]

    # ---------- button handlers ---------------------------------------

    def button_plus(self, event_name, data, kwargs):
        prev = self.idx
        # advance: -1 → 0 → 1 … → last → -1 …
        if self.idx < 0:
            self.idx = 0
        elif self.idx < len(self.sequences) - 1:
            self.idx += 1
        else:
            self.idx = -1
        self.log(f"➕ from {prev} to {self.idx}")

        # turn on the newly selected group (if any)
        if self.idx >= 0:
            for light in self._expand(self.sequences[self.idx]):
                self.call_service("light/turn_on",
                                  entity_id=light,
                                  brightness_pct=60,
                                  transition=2)

    def button_minus(self, event_name, data, kwargs):
        prev = self.idx

        # 1) switch off current group (if any)
        if self.idx >= 0:
            for light in self._expand(self.sequences[self.idx]):
                self.call_service("light/turn_off",
                                  entity_id=light,
                                  transition=2)

        # 2) step back: 4→3→2→1→0→–1 (and stay at –1)
        if self.idx > 0:
            self.idx -= 1
        else:
            self.idx = -1

        # 3) turn on the newly selected (previous) group
        if self.idx >= 0:
            for light in self._expand(self.sequences[self.idx]):
                self.call_service("light/turn_on",
                                  entity_id=light,
                                  brightness_pct=60,
                                  transition=2)

        self.log(f"➖ from {prev} to {self.idx}")


    def button_power(self, event_name, data, kwargs):
        prev = self.idx

        if self.idx < 0:
            # all off  →  all on (jump to last sequence)
            for light in self._all_entity_ids:
                self.call_service("light/turn_on",
                                  entity_id=light,
                                  brightness_pct=60,
                                  transition=2)
            self.idx = len(self.sequences) - 1
        else:
            # anything on → everything off
            for light in self._all_entity_ids:
                self.call_service("light/turn_off",
                                  entity_id=light,
                                  transition=2)
            self.idx = -1

        self.log(f"⏻ from {prev} to {self.idx}")
