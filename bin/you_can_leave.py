#!/usr/bin/env python3

import subprocess
import time
import os
import threading
from pystray import Icon, MenuItem as item, Menu
from PIL import Image
from pynput import keyboard
from functools import partial

bluetooth_connection_check_interval = 5  # Check Bluetooth connection every n seconds
bluetooth_lock_enabled = False  # Start disabled by default
exit_event = False  # Event to signal app termination
bluetooth_lock_running = False  # To track if the Bluetooth lock loop is running
icon = None  # Placeholder for the menu bar icon
selected_device_address = None  # To store the selected Bluetooth device address
device_list = []  # To store available devices


# Function to get connected Bluetooth devices
def get_connected_bluetooth_devices():
    try:
        result = subprocess.run(["blueutil", "--connected"], stdout=subprocess.PIPE)
        devices = result.stdout.decode("utf-8").strip().split("\n")

        device_info = []
        for device in devices:
            if "address" in device:
                address = device.split(",")[0].split(": ")[1]
                name = device.split("name: ")[1].split('"')[1]
                device_info.append((address, name))

        return device_info
    except Exception as e:
        print(f"Error retrieving Bluetooth devices: {e}")
        return []


# Function to check if the Bluetooth device is connected
def check_bluetooth_connection():
    try:
        if not selected_device_address:
            print("No Bluetooth device selected.")
            return False

        result = subprocess.run(
            ["blueutil", "--info", selected_device_address], stdout=subprocess.PIPE
        )
        output = result.stdout.decode("utf-8")

        if "not connected" in output:
            print(f"Bluetooth device {selected_device_address} is disconnected.")
            return False
        elif "connected" in output:
            print(f"Bluetooth device {selected_device_address} is connected.")
            return True
        else:
            print(
                f"Unable to determine Bluetooth connection status for {selected_device_address}."
            )
            return False
    except Exception as e:
        print(f"Error checking Bluetooth connection: {e}")
        return False


# Function to lock the screen
def lock_screen():
    os.system(
        'osascript -e \'tell application "System Events" to keystroke "q" using {control down, command down}\''
    )


# Function to start the Bluetooth monitoring loop
def bluetooth_lock_loop():
    global bluetooth_lock_running, bluetooth_lock_enabled
    bluetooth_lock_running = True
    rebuild_menu()  # Disable the toggle and quit menu while the Bluetooth lock is running

    while bluetooth_lock_enabled and not exit_event:
        if not check_bluetooth_connection():
            print(
                f"Bluetooth device {selected_device_address} disconnected, locking screen..."
            )
            lock_screen()
            # Disable the Bluetooth lock after locking the screen
            bluetooth_lock_enabled = False
            break
        else:
            print(f"Bluetooth device {selected_device_address} connected.")
        time.sleep(bluetooth_connection_check_interval)

    bluetooth_lock_running = False
    update_icon()
    rebuild_menu()  # Re-enable the toggle and quit menu after the lock loop stops


# Function to toggle the Bluetooth lock tool
def toggle_bluetooth_lock():
    global bluetooth_lock_enabled
    if bluetooth_lock_running:
        print("Bluetooth lock is currently running, cannot disable until it finishes.")
        return

    if not selected_device_address:
        print("No Bluetooth device selected. Please select a device first.")
        return

    bluetooth_lock_enabled = not bluetooth_lock_enabled
    update_icon()  # Immediately update the icon before starting the Bluetooth monitoring
    rebuild_menu()  # Rebuild the menu to update the toggle label

    if bluetooth_lock_enabled:
        print(f"Bluetooth lock enabled for device {selected_device_address}.")
        # Run Bluetooth lock loop in a separate thread to avoid blocking the UI
        threading.Thread(target=bluetooth_lock_loop, daemon=True).start()
    else:
        print("Bluetooth lock disabled.")


# Function to select a Bluetooth device
def select_device(device_address, device_name, icon, item):
    global selected_device_address
    selected_device_address = device_address
    print(f"Selected Bluetooth device: {device_name} ({device_address})")
    rebuild_menu()


# Function to refresh the Bluetooth device list
def refresh_devices(icon, item):
    print("Refreshing Bluetooth device list...")
    rebuild_menu()


# Update the menu bar icon when the tool state changes
def update_icon():
    if bluetooth_lock_enabled:
        icon.icon = Image.open("icons/bt_enabled.png")
        icon.title = "You Can Leave: Enabled"
    else:
        icon.icon = Image.open("icons/bt_disabled.png")
        icon.title = "You Can Leave: Disabled"

    # Force refresh by toggling visibility
    if icon.visible:
        icon.visible = False
        icon.visible = True


# Function to rebuild the menu dynamically
def rebuild_menu():
    device_items = []
    global device_list
    device_list = get_connected_bluetooth_devices()

    for device_address, device_name in device_list:
        # Use functools.partial to pass additional arguments
        selected_marker = ">> " if device_address == selected_device_address else ""
        device_items.append(
            item(
                f"{selected_marker}Select {device_name}",
                partial(select_device, device_address, device_name),
                enabled=not bluetooth_lock_enabled,
            )
        )

    # If no device is selected, disable the toggle option
    toggle_label = (
        "Disable Bluetooth Lock" if bluetooth_lock_enabled else "Enable Bluetooth Lock"
    )
    enable_toggle = bool(
        selected_device_address
    )  # Only allow enabling if a device is selected
    if bluetooth_lock_running:
        menu = Menu(
            item(
                toggle_label, toggle_bluetooth_lock, enabled=False
            ),  # Disable menu item while running
            item(
                "Refresh Devices", refresh_devices, enabled=False
            ),  # Disable refresh while running
            item("Quit", quit_app, enabled=False),  # Disable Quit while running
            *device_items,  # Add the dynamically generated device menu items
        )
    else:
        menu = Menu(
            item(toggle_label, toggle_bluetooth_lock, enabled=enable_toggle),
            item("Refresh Devices", refresh_devices),
            item("Quit", quit_app),
            *device_items,  # Add device selection items
        )
    icon.menu = menu


# Function to quit the app
def quit_app(icon, item):
    if bluetooth_lock_running:
        print("Cannot quit the application while Bluetooth lock is running.")
        return
    print("Quitting the application...")
    global exit_event
    exit_event = True
    icon.stop()


# Set up pystray for the menu bar icon
def setup_icon():
    global icon
    icon = Icon("You Can Leave", Image.open("icons/bt_disabled.png"), menu=None)
    rebuild_menu()  # Rebuild the menu with available devices
    icon.run()


# Hotkey handler using pynput
def on_press(key):
    pass


# Set up listener for hotkeys in a separate thread
def listen_hotkey():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# Run the menu bar icon on the main thread
setup_icon()

# Start hotkey listener in a separate thread
hotkey_thread = threading.Thread(target=listen_hotkey, daemon=True).start()

# Keep the script running indefinitely
try:
    while not exit_event:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
