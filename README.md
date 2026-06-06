# PAN Generator — Authorized Penetration Testing

Generate Luhn-valid test credit card numbers from known BINs and partial account numbers.

## Quick Start

```bash
# Clone and run
git clone https://github.com/Fals3Proph3t/card_gen_tester.git
cd card_gen_tester
python3 cardgen.py

# Or run directly from GitHub
curl -sL https://raw.githubusercontent.com/Fals3Proph3t/card_gen_tester/main/cardgen.py | python3
```
# How It Works

1.) You provide known BINs and partial account numbers in cardgen.py
2.) The program fills unknown positions with random digits
3.) It calculates the correct Luhn check digit for the final position
4.) Every generated PAN passes standard Luhn validation

# Supported Card Types
##	Brand	Length	Source
1	Visa	16	Partial PANs
2	Mastercard	16	Partial PANs
3	Amex	15	Partial PANs
4	Discover	16	BIN prefixes

# Customizing BINs
Edit the BRANDS dictionary in cardgen.py:
# Partial PANs (you know some of the account number)
"partials": [
    "427082901528",  # 12 known digits -> 3 filler + 1 check digit
]

# BINs only (just the prefix, rest is random)
"bins": [
    "6011",    # 4-digit BIN -> 11 filler + 1 check digit
    "622126",  # 6-digit BIN -> 9 filler + 1 check digit
    "644",     # 3-digit BIN -> 12 filler + 1 check digit
    "65",      # 2-digit BIN -> 13 filler + 1 check digit
]

# Luhn Algorithm
The Luhn algorithm (mod 10) is a checksum used by all major card networks:

Starting from the rightmost digit, double every second digit
If doubling produces a two-digit number, sum those digits (or subtract 9)
Sum all digits (both doubled and undoubled)
The total must be divisible by 10 for the PAN to be valid
The last digit of the PAN is the "check digit" chosen to make step 4 pass

# Output
1. 4270829015284194
  2. 4270829015282341
  ...
  50. 4270829015288765

  Generated 50 Visa PANs -- Luhn: ALL PASS
