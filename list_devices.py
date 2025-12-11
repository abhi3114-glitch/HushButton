from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

with open("devices_output.txt", "w", encoding="utf-8") as f:
    print("--- Audio Device List ---")
    try:
        devices = AudioUtilities.GetAllDevices()
        for i, device in enumerate(devices):
            try:
                line = f"[{i}] {device.FriendlyName}\n"
                f.write(line)
                print(line.strip())
                
                # Try to get volume interface to check mute state
                mute_state = "Unknown"
                if hasattr(device, 'EndpointVolume'):
                     vol = device.EndpointVolume
                     mute_state = str(vol.GetMute())
                elif hasattr(device, 'Activate'):
                     interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                     vol = cast(interface, POINTER(IAudioEndpointVolume))
                     mute_state = str(vol.GetMute())
                
                f.write(f"    Muted: {mute_state}\n")
                print(f"    Muted: {mute_state}")

            except Exception as e:
                f.write(f"    Error inspecting: {e}\n")
    except Exception as e:
        f.write(f"Fatal Error: {e}\n")
