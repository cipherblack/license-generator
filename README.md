# License Manager

## Overview
This Python script provides a license management system that allows you to:
- Generate unique license keys.
- Sign and store license keys in an SQLite database.
- Verify license keys using RSA encryption.
- Revoke licenses when necessary.
- Manage license validity periods.

The script supports command-line arguments for ease of use.

## Features
- Uses RSA key pair for signing and verification.
- Stores licenses in an SQLite database.
- Allows license expiration handling.
- Supports revoking of licenses.

## Installation
Ensure you have Python 3 installed, then install the required dependencies:

```sh
pip install cryptography
```

## Usage
Run the script with the following options:

### Initialize Database and Generate RSA Keys
```sh
python license_manager.py --initialize
```

### Generate a New License
```sh
python license_manager.py --generate --length 16 --duration 30
```
- `--length`: Length of the license key (default: 16 characters)
- `--duration`: Validity duration in days (default: 30 days)

### Verify a License
```sh
python license_manager.py --verify LICENSE_KEY
```

### Revoke a License
```sh
python license_manager.py --revoke LICENSE_KEY
```

## How It Works
1. **Initialization**: Creates an SQLite database and generates RSA key pairs.
2. **License Generation**: Generates a random license key, signs it with a private key, and stores it in the database.
3. **License Verification**: Checks if a license is valid by verifying its signature and expiration date.
4. **License Revocation**: Marks a license as revoked in the database.

## License
This project is open-source. Feel free to modify and use it as needed.

