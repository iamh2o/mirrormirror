import CoreLocation
import objc
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def get_location():
    # Initialize CoreLocation manager and delegate
    location_manager = CoreLocation.CLLocationManager.alloc().init()

    # Request authorization and start location updates
    location_manager.requestWhenInUseAuthorization()
    logging.info("Location services enabled. Starting updates...")
    location_manager.startUpdatingLocation()

    # Wait for location to be updated initially
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


# Fetch location
if __name__ == "__main__":
    location = get_location()
    if location:
        print(f"Your current location is approximately: {location}")
    else:
        print("Failed to get the location.")
