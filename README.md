
# License Generator Project

This project is designed to create and validate software licenses using cryptographic techniques. The license generator creates unique license keys that can be used to secure and validate the usage of a software product.

## Features

- **License Generation:** Generates a unique license key for each user or installation.
- **License Validation:** Verifies the validity of a license key using cryptographic techniques.
- **SQLite Database Integration:** Stores generated licenses in an SQLite database for persistence and validation.

## Requirements

To run this project, you need the following:
- Python 3.x
- Required libraries:
  - `cryptography`
  - `sqlite3`

Install the dependencies using pip:

```bash
pip install cryptography
```

## Usage

### Clone the repository

```bash
git clone https://github.com/cipherblack/license-generator.git
```

### Navigate to the project directory:

```bash
cd license-generator
```

### Run the license generation script:

```bash
python generate_license.py
```

### Example of how to validate a license:

```bash
python validate_license.py LICENSE_KEY
```

### Example Code:

```python
from cryptography_module import LicenseGenerator

# Example of generating a license
license_generator = LicenseGenerator()
new_license = license_generator.generate_license()
print("Generated License:", new_license)

# Example of validating a license
is_valid = license_generator.validate_license(new_license)
print("License Valid:", is_valid)
```

## How It Works

### License Generation

The license is generated using a cryptographic algorithm (such as RSA or AES) and a unique identifier for the user. The generated license is then stored in an SQLite database.

### License Validation

When the license is used, it is validated against the stored licenses in the database to ensure it is valid and hasn’t been tampered with.

## Database

The project uses an SQLite database to store the generated licenses. The database schema is simple, consisting of a table to store:

- License key
- Creation date
- Expiration date (optional)
- Validity status

## License

This project is licensed under the MIT License
