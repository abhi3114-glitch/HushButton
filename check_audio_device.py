from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

try:
    devices = AudioUtilities.GetSpeakers()
    print(f"Devices Object: {devices}")
    
    # Try to get name
    if hasattr(devices, 'FriendlyName'):
        print(f"Device Name: {devices.FriendlyName}")
    
    # If it's a wrapper, it might have an ID
    if hasattr(devices, 'id'):
        print(f"Device ID: {devices.id}")
        
    # Check mute state
    if hasattr(devices, 'Activate'):
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    elif hasattr(devices, 'EndpointVolume'):
        interface = devices.EndpointVolume
    else:
        interface = None
        print("Could not get interface")

    if interface:
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        print(f"Current Mute State (from API): {volume.GetMute()}")
        print(f"Current Volume (Scalar): {volume.GetMasterVolumeLevelScalar()}")

except Exception as e:
    print(f"Error: {e}")
