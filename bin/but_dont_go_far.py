import time
import os
import sys
import math
import threading
import logging
from pystray import Icon, MenuItem as item, Menu
from PIL import Image
from pynput import keyboard
import CoreLocation
import objc


# sys.argv[1] = distance_threshold in km, can be float
if len(sys.argv) < 2:
    print("Usage: python but_dont_go_far.py <distance_threshold in km, float>")
    sys.exit(1)
    
# Setup logging
logging.basicConfig(
    filename="distance_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

wait_time_to_check_location = 10  # Check location every n seconds
distance_monitor_enabled = False  # Start disabled by default
exit_event = False  # Event to signal app termination
distance_monitor_running = False  # To track if the distance monitor loop is running
icon = None  # Placeholder for the menu bar icon
current_location = None  # Store current location
initial_location = None  # Store the initial location (lat, long)
distance_threshold = (
    float(sys.argv[1]) if len(sys.argv) > 1 else None
)  # Distance threshold from command-line argument

location_manager = None  # Global location manager instance


# Function to get the current location
def get_location():
    # Initialize CoreLocation manager
    location_manager = CoreLocation.CLLocationManager.alloc().init()
    # Request authorization and start location updates
    location_manager.requestWhenInUseAuthorization()
    logging.info("Location services enabled. Starting updates...")
    location_manager.startUpdatingLocation()

    # Wait for location to be updated
    time.sleep(5)

    # Try to retrieve the location 5 times before failing
    attempts = 5
    for attempt in range(1, attempts + 1):
        coords = location_manager.location()
        if coords:
            coords = coords.coordinate()
            lat = coords.latitude
            longitude = coords.longitude
            logging.info(f"Location retrieved on attempt {attempt}: {lat}, {longitude}")
            return (lat, longitude)
        else:
            logging.info(f"Waiting for location update... Attempt {attempt}")
            time.sleep(1)  # Wait for 1 second before retrying

    logging.error("Failed to get the location after 5 attempts.")
    return None


# Function to calculate distance between two lat/long points (Haversine formula)
def calculate_distance(loc1, loc2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
    lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers


# Function to lock the screen
def lock_screen():
    logging.info("Locking the screen...")
    os.system(
        'osascript -e \'tell application "System Events" to keystroke "q" using {control down, command down}\''
    )


# Function to start monitoring the distance
def distance_monitor_loop():
    global distance_monitor_running, distance_monitor_enabled, initial_location, current_location
    distance_monitor_running = True
    rebuild_menu()  # Disable the toggle and quit menu while monitoring is running

    logging.info(f"Starting location monitoring. Initial location: {initial_location}")

    last_distance_moved = 0
    while distance_monitor_enabled and not exit_event:
        new_location = get_location()  # Use refactored get_location function

        print(
            f"New location: {new_location}, Start location: {initial_location}, Distance Moved: {last_distance_moved}"
        )
        rebuild_menu(current_loc=new_location) 
        if new_location:
            current_location = new_location
            distance_moved = calculate_distance(initial_location, current_location)
            last_distance_moved = distance_moved
            logging.info(
                f"Checking location. Current location: {current_location}, Distance moved: {distance_moved} km"
            )

            if distance_moved > distance_threshold:
                logging.info(
                    f"Exceeded distance threshold of {distance_threshold} km. Locking screen..."
                )
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
    global distance_monitor_enabled, initial_location, current_location
    if distance_monitor_running:
        logging.info(
            "Distance monitor is currently running, cannot disable until it finishes."
        )
        return

    if distance_threshold is None:
        logging.warning("Cannot start distance monitoring. Distance threshold not set.")
        return

    distance_monitor_enabled = not distance_monitor_enabled
    update_icon()  # Immediately update the icon before starting the distance monitoring
    rebuild_menu()  # Rebuild the menu to update the toggle label

    if distance_monitor_enabled:
        logging.info("Distance monitor enabled.")
        initial_location = get_location()  # Use refactored get_location function
        if initial_location:
            logging.info(f"Initial location: {initial_location}")
            threading.Thread(target=distance_monitor_loop, daemon=True).start()
        else:
            logging.error("Failed to get initial location. Disabling monitor.")
            distance_monitor_enabled = False
    else:
        logging.info("Distance monitor disabled.")


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
def rebuild_menu(current_loc='n/a',dist_moved='n/a'):
    global initial_location, current_location
    toggle_label = (
        "Disable Distance Monitor"
        if distance_monitor_enabled
        else "Enable Distance Monitor"
    )
    enable_toggle = (
        distance_threshold is not None
    )  # Only allow enabling if a threshold is set

    # Display the threshold, initial location, and current location
    initial_loc_str = (
        f"Initial Location: {initial_location}"
        if initial_location
        else "Initial Location: N/A"
    )
    current_loc_str = (
        f"Current Location: {current_loc}"
        if current_loc
        else "Current Location: N/A"
    )

    # Calculate distance moved from initial location if both locations are available
    if current_location not in (None, 'n/a'):
        distance_moved = calculate_distance(initial_location, current_location)
        distance_moved_str = f"Distance Moved: {distance_moved:.2f} km"
    else:
        distance_moved_str = "Distance Moved: N/A"

    threshold_str = f"Distance Threshold: {distance_threshold} km"

    if distance_monitor_running:
        menu = Menu(
            item(
                toggle_label, toggle_distance_monitor, enabled=False
            ),  # Disable menu item while running
            item(
                threshold_str, lambda: None, enabled=False
            ),  # Show the threshold value
            item(
                initial_loc_str, lambda: None, enabled=False
            ),  # Show the initial location
            item(
                current_loc_str, lambda: None, enabled=False
            ),  # Show the current location
            item(
                distance_moved_str, lambda: None, enabled=False
            ),  # Show the distance moved
            item("Quit", quit_app, enabled=False),  # Disable Quit while running
        )
    else:
        menu = Menu(
            item(toggle_label, toggle_distance_monitor, enabled=enable_toggle),
            item(threshold_str, lambda: None, enabled=False),
            item(initial_loc_str, lambda: None, enabled=False),
            item(current_loc_str, lambda: None, enabled=False),
            item(
                distance_moved_str, lambda: None, enabled=False
            ),  # Show the distance moved
            item("Quit", quit_app),
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
