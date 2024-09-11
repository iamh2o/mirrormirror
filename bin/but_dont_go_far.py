#!/usr/bin/env python3

import time
import os
import requests
import math
import threading
import logging
from pystray import Icon, MenuItem as item, Menu
from PIL import Image
from pynput import keyboard

# Setup logging
logging.basicConfig(filename="distance_monitor.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

wait_time_to_check_location = 10  # Check location every n seconds
distance_monitor_enabled = False  # Start disabled by default
exit_event = False  # Event to signal app termination
distance_monitor_running = False  # To track if the distance monitor loop is running
icon = None  # Placeholder for the menu bar icon
current_location = None  # Store current location
distance_threshold = None  # Set when the tool is activated

# Function to get the current location using an IP geolocation API
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io/loc")
        return tuple(map(float, response.text.strip().split(',')))  # Latitude, Longitude
    except Exception as e:
        logging.error(f"Error getting location: {e}")
        return None

# Function to calculate distance between two lat/long points (Haversine formula)
def calculate_distance(loc1, loc2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
    lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers

# Function to lock the screen
def lock_screen():
    logging.info("Locking the screen...")
    os.system("osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'")

# Function to start monitoring the distance
def distance_monitor_loop():
    global distance_monitor_running, distance_monitor_enabled
    distance_monitor_running = True
    rebuild_menu()  # Disable the toggle and quit menu while monitoring is running

    logging.info(f"Starting location monitoring. Initial location: {current_location}")

    while distance_monitor_enabled and not exit_event:
        new_location = get_current_location()
        if new_location:
            distance_moved = calculate_distance(current_location, new_location)
            logging.info(f"Current location: {new_location}, Distance moved: {distance_moved} km")
            if distance_moved > distance_threshold:
                logging.info(f"Exceeded distance threshold of {distance_threshold} km. Locking screen...")
                time.sleep(15)  # Warning delay
                lock_screen()
                # Disable the distance monitor after locking the screen
                distance_monitor_enabled = False
                break
        else:
            logging.warning("Unable to get new location.")
        time.sleep(wait_time_to_check_location)

    distance_monitor_running = False
    update_icon()
    rebuild_menu()  # Re-enable the toggle and quit menu after monitoring stops

# Function to toggle distance monitoring
def toggle_distance_monitor():
    global distance_monitor_enabled, current_location
    if distance_monitor_running:
        logging.info("Distance monitor is currently running, cannot disable until it finishes.")
        return

    distance_monitor_enabled = not distance_monitor_enabled
    update_icon()  # Immediately update the icon before starting the distance monitoring
    rebuild_menu()  # Rebuild the menu to update the toggle label

    if distance_monitor_enabled:
        logging.info("Distance monitor enabled.")
        current_location = get_current_location()
        if current_location:
            threading.Thread(target=distance_monitor_loop, daemon=True).start()
        else:
            logging.error("Failed to get current location. Disabling monitor.")
            distance_monitor_enabled = False
    else:
        logging.info("Distance monitor disabled.")

# Function to set the distance threshold
def set_distance_threshold():
    global distance_threshold
    try:
        threshold = float(input("Enter the distance threshold (in kilometers): "))
        distance_threshold = threshold
        logging.info(f"Distance threshold set to {distance_threshold} km.")
        rebuild_menu()  # Update menu after setting threshold
    except ValueError:
        logging.error("Invalid input for distance threshold.")
        distance_threshold = None

# Update the menu bar icon when the tool state changes
def update_icon():
    if distance_monitor_enabled:
        icon.icon = Image.open("icons/gf_enabled.png")
        icon.title = "But Don't Go Far: Enabled"
    else:
        icon.icon = Image.open("icons/gf_disabled.png")
        icon.title = "But Don't Go Far: Disabled"

    # Force refresh by toggling visibility
    if icon.visible:
        icon.visible = False
        icon.visible = True

# Function to rebuild the menu dynamically
def rebuild_menu():
    toggle_label = 'Disable Distance Monitor' if distance_monitor_enabled else 'Enable Distance Monitor'
    enable_toggle = distance_threshold is not None  # Only allow enabling if a threshold is set
    if distance_monitor_running:
        menu = Menu(
            item(toggle_label, toggle_distance_monitor, enabled=False),  # Disable menu item while running
            item('Set Distance Threshold', set_distance_threshold, enabled=False),  # Disable setting threshold while running
            item('Quit', quit_app, enabled=False)  # Disable Quit while running
        )
    else:
        menu = Menu(
            item(toggle_label, toggle_distance_monitor, enabled=enable_toggle),
            item('Set Distance Threshold', set_distance_threshold),
            item('Quit', quit_app)
        )
    icon.menu = menu

# Function to quit the app
def quit_app(icon, item):
    if distance_monitor_running:
        logging.info("Cannot quit the application while distance monitor is running.")
        return
    logging.info("Quitting the application...")
    global exit_event
    exit_event = True
    icon.stop()

# Set up pystray for the menu bar icon
def setup_icon():
    global icon
    icon = Icon("But Don't Go Far", Image.open("icons/gf_disabled.png"), menu=None)
    rebuild_menu()  # Rebuild the menu with available options
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
    logging.info("Exiting...")
