# GNOME-Network
Global muon detection network using UNO-R3 (more options soon)


# GNOME — Global Network Of Muon Explorers

## What is this?
A global citizen science network of low cost 
particle detectors built from Arduino boards.
Each node detects cosmic ray muon hits and logs 
them to a central cloud database.

By correlating simultaneous hits across thousands 
of nodes worldwide we hope to detect patterns 
that might indicate dark matter wind interactions.

## Cost per node
~$5 using parts you may already have

## Parts needed
- Arduino UNO R3
- Any standard LED (used reversed)
- Electrical tape
- USB cable or 9V battery
- Laptop with Python for uploading

## Wiring
- LED long leg → GND
- LED short leg → A0
- Wrap LED completely in electrical tape

## Software setup
1. Upload arduino/gnome_detector.ino
2. Edit NODE_ID, LATITUDE, LONGITUDE, ELEVATION
3. pip install pyserial requests
4. Edit SHEETS_URL in python/gnome_logger.py
5. Run python/gnome_logger.py

## How it works
- Detector runs standalone on 9V battery
- Saves hits to onboard EEPROM memory
- When connected to laptop uploads automatically
- Data sent to global Google Sheets database
- Recalibrates automatically every hour

## Join the network
Open an Issue using the Node Registration template

## Science background
Cosmic ray muons pass through everything including
you right now at 10,000 per minute. Dark matter
may travel in streams called dark matter wind.
A global network of detectors could reveal these
patterns through correlated simultaneous hits.

## License
MIT License — open source forever
