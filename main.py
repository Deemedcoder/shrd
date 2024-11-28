import socket
import sqlite3
import time  # Import time module
from datetime import datetime

# Set up the UDP server
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 8888  # Same port as the Arduino is sending to

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY,
        current_humidity INTEGER,
        current_temperature INTEGER,
        set_temperature INTEGER,
        set_humidity INTEGER,
        front_door_status INTEGER,
        back_door_status INTEGER,
        relay_status INTEGER,
        ups_status INTEGER,
        fire_status INTEGER,
        timestamp TEXT
    )
''')
conn.commit()

while True:
    # Receive message from the Arduino
    data, addr = sock.recvfrom(2048)  # buffer size is 1024 bytes
    print(f"Received message: {data.decode()}")
    
    # Extract values from the string (e.g., "6423299900001")
    received_data = data.decode().strip()

    # Assuming the string format is as follows:
    # First 2 values are current humidity
    # Next 2 are current temperature
    # Next 2 are set temperature
    # Next 2 are set humidity
    # Then each value is a status value (1 byte for each)

    current_humidity = int(received_data[0:2])
    current_temperature = int(received_data[2:4])
    set_temperature = int(received_data[4:6])
    set_humidity = int(received_data[6:8])
    front_door_status = int(received_data[8:9])
    back_door_status = int(received_data[9:10])
    relay_status = int(received_data[10:11])
    ups_status = int(received_data[11:12])
    fire_status = int(received_data[12:13])

    # Get current timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Print values
    print(f"Current Humidity: {current_humidity}")
    print(f"Current Temperature: {current_temperature}")
    print(f"Set Temperature: {set_temperature}")
    print(f"Set Humidity: {set_humidity}")
    print(f"Front Door Status: {front_door_status}")
    print(f"Back Door Status: {back_door_status}")
    print(f"Relay Status: {relay_status}")
    print(f"UPS Status: {ups_status}")
    print(f"Fire Status: {fire_status}")
    print(f"Timestamp: {current_timestamp}")

    # Update the data in the database (if id=1 exists)
    cursor.execute('''
        SELECT COUNT(*) FROM sensor_data WHERE id = 1
    ''')
    row_count = cursor.fetchone()[0]

    if row_count == 0:
        # Insert data if id=1 doesn't exist
        cursor.execute('''
            INSERT INTO sensor_data (
                id, current_humidity, current_temperature, set_temperature, 
                set_humidity, front_door_status, back_door_status, 
                relay_status, ups_status, fire_status, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1, current_humidity, current_temperature, set_temperature, 
              set_humidity, front_door_status, back_door_status, 
              relay_status, ups_status, fire_status, current_timestamp))
    else:
        # Update data if id=1 exists
        cursor.execute('''
            UPDATE sensor_data SET 
                current_humidity = ?, current_temperature = ?, 
                set_temperature = ?, set_humidity = ?, 
                front_door_status = ?, back_door_status = ?, 
                relay_status = ?, ups_status = ?, 
                fire_status = ?, timestamp = ?
            WHERE id = 1
        ''', (current_humidity, current_temperature, set_temperature, 
              set_humidity, front_door_status, back_door_status, 
              relay_status, ups_status, fire_status, current_timestamp))

    # Commit the transaction
    conn.commit()

    # Optional: Add a delay to avoid overwhelming the console or database
    time.sleep(1)
