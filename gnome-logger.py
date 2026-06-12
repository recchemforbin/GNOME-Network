import serial
import serial.tools.list_ports
import requests
import json
import time
import os
from datetime import datetime

# ═══════════════════════════════
# CONFIGURE THESE
# ═══════════════════════════════
SHEETS_URL = "https://script.google.com/macros/s/AKfycbwHpRiuIYJ3olvqe_TNCjUorQyJUuNN2VubdC6ATfI9wynSZQoy7zQNqmJvfAy9M-E5/exec"
NODE_ID    = "GNOME-001"
LOG_FILE   = "gnome_hits.csv"

def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        if any(x in desc for x in ["arduino", "ch340", "usb serial", "uart"]):
            return port.device
    return None

def send_to_sheets(data):
    try:
        response = requests.post(
            SHEETS_URL,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.text == "OK"
    except Exception as e:
        print(f"Cloud error: {e}")
        return False

def save_to_local_log(data):
    # Also save locally as backup
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        if not file_exists:
            f.write("timestamp,hit_number,spike,baseline,latitude,longitude,elevation,node_id,received\n")
        f.write(f"{data['timestamp']},{data['hit_number']},{data['spike']},{data['baseline']},{data['latitude']},{data['longitude']},{data['elevation']},{data['node_id']},{datetime.now()}\n")

def parse_hit(line, hit_type):
    try:
        parts = line.strip().split(",")
        # Remove HIT or STORED prefix
        if parts[0] in ["HIT", "STORED"]:
            parts = parts[1:]
        if len(parts) == 8:
            return {
                "type":       "hit",
                "timestamp":  parts[0],
                "hit_number": parts[1],
                "spike":      parts[2],
                "baseline":   parts[3],
                "latitude":   parts[4],
                "longitude":  parts[5],
                "elevation":  parts[6],
                "node_id":    parts[7].strip(),
                "hit_type":   hit_type
            }
    except Exception as e:
        print(f"Parse error: {e}")
    return None

def main():
    print("╔═══════════════════════╗")
    print("║  GNOME LOGGER v1.0    ║")
    print("╚═══════════════════════╝")
    print(f"Node: {NODE_ID}")
    print(f"Log file: {LOG_FILE}")
    print("Looking for Arduino...")

    # Keep trying to find Arduino
    ser = None
    while ser is None:
        port = find_arduino()
        if port:
            try:
                ser = serial.Serial(port, 9600, timeout=1)
                print(f"Arduino found on {port}")
            except Exception as e:
                print(f"Connection error: {e}")
                time.sleep(2)
        else:
            print("Arduino not found, retrying in 5 seconds...")
            time.sleep(5)

    total_uploaded = 0
    total_live     = 0

    while True:
        try:
            line = ser.readline().decode("utf-8").strip()

            if not line:
                continue

            print(f">> {line}")

            # Handle stored hits from EEPROM
            if line.startswith("STORED,"):
                hit = parse_hit(line, "stored")
                if hit:
                    success = send_to_sheets(hit)
                    save_to_local_log(hit)
                    total_uploaded += 1
                    status = "✓" if success else "✗"
                    print(f"{status} Stored hit {hit['hit_number']} uploaded")

            # Handle live hits
            elif line.startswith("HIT,"):
                hit = parse_hit(line, "live")
                if hit:
                    success = send_to_sheets(hit)
                    save_to_local_log(hit)
                    total_live += 1
                    status = "✓" if success else "✗"
                    print(f"{status} Live hit {hit['hit_number']} | Spike: {hit['spike']}")

            # Status messages
            elif "UPLOAD_END" in line:
                print(f"═══ Upload complete: {total_uploaded} stored hits sent ═══")

            elif "DETECTION ACTIVE" in line:
                print("═══ Live detection started ═══")

        except KeyboardInterrupt:
            print(f"\nGNOME Logger stopped")
            print(f"Stored hits uploaded: {total_uploaded}")
            print(f"Live hits logged: {total_live}")
            ser.close()
            break

        except serial.SerialException:
            print("Arduino disconnected! Waiting to reconnect...")
            ser = None
            while ser is None:
                time.sleep(3)
                port = find_arduino()
                if port:
                    try:
                        ser = serial.Serial(port, 9600, timeout=1)
                        print(f"Reconnected on {port}")
                    except:
                        pass

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()