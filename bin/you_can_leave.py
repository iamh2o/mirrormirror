#!/usr/bin/env python3

import subprocess
import time
import os
import keyboard
import threading
from pystray import Icon, MenuItem as item, Menu
from PIL import Image

# Bluetooth device address (replace with your device's MAC address)
DEVICE_ADDRESS = "XX-XX-XX-XX-XX-XX"
bluetooth_lock_enabled = False  # Start disabled by default
icon = None  # Placeholder for the menu bar icon

# Function to check if Bluetooth device is connected
def check_bluetooth_connection():
    try:
        result = subprocess.run(["blueutil", "--connected", DEVICE_ADDRESS], stdout=subprocess.PIPE)
        return "0" in result.stdout.decode('utf-8')  # If the result is "0", the device is disconnected
    except Exception as e:
        print(f"Error checking Bluetooth connection: {e}")
        return False

# Function to lock the screen
def lock_screen():
    os.system("osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'")

# Function to start the Bluetooth monitoring loop
def bluetooth_lock_loop():
    global bluetooth_lock_enabled
    while bluetooth_lock_enabled:
        if check_bluetooth_connection():
            print("Bluetooth device disconnected, locking screen...")
            lock_screen()
            break
        else:
            print("Bluetooth device connected.")
        time.sleep(60)

# Function to toggle the Bluetooth lock tool
def toggle_bluetooth_lock():
    global bluetooth_lock_enabled
    bluetooth_lock_enabled = not bluetooth_lock_enabled
    print("Bluetooth lock enabled" if bluetooth_lock_enabled else "Bluetooth lock disabled")

    if bluetooth_lock_enabled:
        threading.Thread(target=bluetooth_lock_loop).start()
    update_icon()

# Update the menu bar icon when the tool state changes
def update_icon():
    if bluetooth_lock_enabled:
        icon.icon = Image.open("enabled_icon.png")
        icon.title = "You Can Leave: Enabled"
    else:
        icon.icon = Image.open("disabled_icon.png")
        icon.title = "You Can Leave: Disabled"

# Function to quit the app
def quit_app(icon, item):
    icon.stop()

# Set up pystray for the menu bar icon
def setup_icon():
    global icon
    menu = Menu(
        item('Toggle Bluetooth Lock', toggle_bluetooth_lock),
        item('Quit', quit_app)
    )
    icon = Icon("You Can Leave", Image.open("disabled_icon.png"), menu=menu)
    icon.run()

# Hotkey to toggle the Bluetooth lock (Command + Shift + B)
keyboard.add_hotkey('cmd+shift+b', toggle_bluetooth_lock)

# Run the menu bar icon in a separate thread
threading.Thread(target=setup_icon).start()

# Keep the script running indefinitely
keyboard.wait()