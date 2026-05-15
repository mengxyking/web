import subprocess
import time


def get_connected_devices():
    # Run the adb devices command
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = result.stdout.strip().split('\n')[1:]  # Skip the first line (header)

    connected_devices = []
    for device in devices:
        if device.strip():
            device_info = device.split('\t')
            connected_devices.append((device_info[0], device_info[1]))  # (device_id, status)

    return connected_devices


def monitor_devices():
    known_devices = set()

    while True:
        current_devices = get_connected_devices()
        current_device_ids = {device[0] for device in current_devices}

        # Check for new connections
        new_devices = current_device_ids - known_devices
        for device_id in new_devices:
            print(f"Device connected: {device_id}")

        # Check for disconnections
        disconnected_devices = known_devices - current_device_ids
        for device_id in disconnected_devices:
            print(f"Device disconnected: {device_id}")

        # Update the known devices set
        known_devices = current_device_ids

        time.sleep(5)  # Check every 5 seconds


if __name__ == "__main__":
    monitor_devices()