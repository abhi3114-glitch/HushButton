from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class AudioController:
    def __init__(self):
        self.volume = None
        self.current_device_index = 0
        self.devices = []
        self.simulated = False
        self.refresh_devices()
        try:
            self.set_default_mic()
        except:
             # Fallback if 0 fail
             self._set_simulated()

    def refresh_devices(self):
        """Scans for active input (microphone) devices."""
        self.devices = []
        try:
             # Use low level API to find Capture devices specifically if possible, 
             # but GetAllDevices returns all. We can check the data flow or just list all.
             # Ideally we want microphones.
             all_devs = AudioUtilities.GetAllDevices()
             for i, dev in enumerate(all_devs):
                 try:
                     # Check if it's a capture device? 
                     # dev.state is active, but we need Flow.
                     # For now, let's just list everything but try to default to Mic.
                     
                     if hasattr(dev, 'Activate'):
                         dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                     elif hasattr(dev, 'EndpointVolume'):
                          _ = dev.EndpointVolume
                     else:
                          continue
                     
                     name = dev.FriendlyName
                     self.devices.append({"index": i, "name": name, "object": dev})
                 except:
                     pass
        except:
             pass
        
        if not self.devices:
             self.devices.append({"index": -1, "name": "No Devices Found", "object": None})

    def get_devices_list(self):
        return [d["name"] for d in self.devices]

    def set_device(self, list_index):
        if list_index < 0 or list_index >= len(self.devices):
            return
            
        dev_entry = self.devices[list_index]
        self.current_device_index = list_index
        
        if dev_entry["object"] is None:
             self._set_simulated()
             return

        try:
            device = dev_entry["object"]
            interface = None
            if hasattr(device, 'Activate'):
                interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            elif hasattr(device, 'EndpointVolume'):
                interface = device.EndpointVolume
            
            if interface:
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                self.simulated = False
            else:
                 raise Exception("No Interface")
        except Exception as e:
            print(f"Failed to set device: {e}")
            self._set_simulated()
            
    def set_default_mic(self):
        """Sets the volume control to the default system microphone."""
        try:
            from pycaw.api.mmdeviceapi import MMDeviceEnumerator, EDataFlow, ERole
            device_enumerator = MMDeviceEnumerator()
            # EDataFlow.eCapture = 1, ERole.eMultimedia = 1
            device = device_enumerator.GetDefaultAudioEndpoint(1, 1)
            
            # Find this device in our list to sync UI
            target_id = device.id
            found_idx = -1
            for idx, d in enumerate(self.devices):
                if hasattr(d["object"], "id") and d["object"].id == target_id:
                    found_idx = idx
                    break
            
            if found_idx != -1:
                self.set_device(found_idx)
            else:
                # Just set it directly if not in list
                if hasattr(device, 'Activate'):
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                elif hasattr(device, 'EndpointVolume'):
                    interface = device.EndpointVolume
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                self.simulated = False
                
        except Exception as e:
            print(f"Start default mic failed: {e}")
            self.set_device(0) # Fallback

    def _set_simulated(self):
        print("Switching to SIMULATION MODE.")
        self.simulated = True
        self._muted_sim = False
        self.volume = None

    def _get_volume_interface(self):
         # Legacy helper not used anymore
         pass

    def mute(self):
        """Mutes the master volume."""
        if self.simulated:
            print("[SIM] Muting System")
            self._muted_sim = True
            return
        self.volume.SetMute(1, None)

    def unmute(self):
        """Unmutes the master volume."""
        if self.simulated:
            print("[SIM] Unmuting System")
            self._muted_sim = False
            return
        self.volume.SetMute(0, None)

    def toggle_mute(self):
        """Toggles the current mute state."""
        currentState = self.is_muted()
        if currentState:
            self.unmute()
            return False
        else:
            self.mute()
            return True

    def is_muted(self):
        """Returns True if currently muted, False otherwise."""
        if self.simulated:
            return self._muted_sim
        try:
            return bool(self.volume.GetMute())
        except:
             return False

if __name__ == "__main__":
    ac = AudioController()
    print(f"Muted: {ac.is_muted()}")
