# Forensic Datasets Guide

To use this Advanced Digital Forensics System, you need a disk image file (RAW `.dd` or EnCase `.E01`). Real-world disk images can be very large (gigabytes).

## Where to find datasets

1. **Digital Corpora (Highly Recommended)**
   - Link: https://digitalcorpora.org/
   - Digital Corpora hosts various disk images. For testing, the "M57 Patents" scenario or "Lone Wolf" scenario are great.
   
2. **NIST CFReDS (Computer Forensic Reference Data Sets)**
   - Link: https://cfreds.nist.gov/
   - CFReDS provides specific images for testing file recovery, hashing, and steganography.
   - Look for the "Data Leakage Case" or "Hacking Case".

3. **Kaggle**
   - Link: https://www.kaggle.com/
   - Search for "digital forensics disk image" or "steganography dataset".

## Instructions for testing

1. Download a `.dd` (RAW) or `.E01` file from one of the sources above.
2. Place the downloaded file in a known directory (e.g., `C:\Users\vpraj\Downloads\test_image.dd`).
3. Open the **Covert Data Detection System** web dashboard.
4. Paste the path to the disk image in the "Disk Image Path" input box.
5. Click "INITIALIZE SCAN".

## Simulating a Small Disk Image

If you want to test the script without downloading a massive file, you can create a small simulated disk image (RAW format) using Linux (`dd if=/dev/urandom of=fake_image.dd bs=1M count=50`) or by analyzing an existing small `.img` file (like a floppy disk image or a Raspberry Pi boot image).
