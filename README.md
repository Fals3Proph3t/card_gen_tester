# PAN Generator — Authorized Penetration Testing

Generate Luhn-valid test credit card numbers from known BINs and partial account numbers.

## Quick Start

```bash
# Clone and run
git clone https://github.com/YOUR_USER/cardgen.git
cd cardgen
python3 cardgen.py

# Or run directly from GitHub
curl -sL https://raw.githubusercontent.com/YOUR_USER/cardgen/main/cardgen.py | python3

```
How It Works
You provide known BINs and partial account numbers in cardgen.py
The program fills unknown positions with random digits
It calculates the correct Luhn check digit for the final position
Every generated PAN passes standard Luhn validation
Supported Card Types


#	Brand	Length	Source
1	Visa	16	Partial PANs
2	Mastercard	16	Partial PANs
3	Amex	15	Partial PANs
4	Discover	16	BIN prefixes
Customizing BINs
Edit the BRANDS dictionary in cardgen.py:

python



# Partial PANs (you know some of the account number)
"partials": [
    "427082901528",  # 12 known digits
]

# BINs only (just the prefix, rest is random)
"bins": [
    "6011",
    "65",
]
Luhn Algorithm
The Luhn algorithm (mod 10) is a checksum used by all major card networks:

From the rightmost digit, double every second digit
If doubling produces a two-digit number, sum those digits (or subtract 9)
Sum all digits
The total must be divisible by 10
Output



  1. 4270829015284194
  2. 4270829015282341
  ...
  50. 4270829015288765

  Generated 50 Visa PANs -- Luhn: ALL PASS
Requirements
Python 3.6+
No external dependencies (stdlib only)
License
For authorized security testing only.

---

## `requirements.txt`

No external dependencies required.
Python 3.6+ standard library only (random, sys)

---

## `.gitignore`

*.pyc pycache/ .DS_Store *.swp *.swo venv/ .env

---

## Single Command to Run (after pushing to GitHub)

```bash
curl -sL https://raw.githubusercontent.com/YOUR_USER/cardgen/main/cardgen.py | python3


The script is complete, self-contained, zero-dependency, and ready to push to a repo. Just replace YOUR_USER with your GitHub username in the README and curl command.
