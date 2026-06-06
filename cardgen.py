#!/usr/bin/env python3
"""
CardGen — Luhn-Valid Test Credit Card Generator
For authorized penetration testing only.

Usage:
    python3 cardgen.py

Generates valid test cards for:
  - Visa (16-digit, BIN 4xxxxx)
  - Mastercard (16-digit, BINs 51xx-55xx, 2221-2720)
  - Discover (16-digit, BINs 6011, 622126-622925, 644-649, 65xx)
  - American Express (15-digit, BINs 34xx, 37xx)

All numbers pass Luhn algorithm verification.
All expiry dates are future-dated.
"""

import random
import sys
from datetime import datetime, timedelta


# ──────────────────────────────────────────────
#  LUHN CHECK DIGIT CALCULATION
# ──────────────────────────────────────────────

def luhn_check_digit(partial: str) -> int:
    """
    Given a partial card number (without check digit),
    returns the Luhn check digit needed to make it valid.
    """
    digits = [int(d) for d in partial]
    # Double every second digit from the right
    for i in range(len(digits) - 1, -1, -2):
        doubled = digits[i] * 2
        digits[i] = doubled if doubled < 10 else doubled - 9
    total = sum(digits)
    return (10 - (total % 10)) % 10


def generate_full_number(prefix: str, total_length: int) -> str:
    """
    Generate a full card number from a given prefix.
    - prefix: first N digits (fewer than total_length)
    - total_length: full card length (15 for Amex, 16 for others)
    """
    remaining = total_length - len(prefix) - 1  # -1 for check digit
    if remaining < 0:
        raise ValueError(f"Prefix {prefix} is too long for {total_length}-digit card")
    # Fill remaining digits randomly (excluding check digit position)
    partial = prefix + ''.join(str(random.randint(0, 9)) for _ in range(remaining))
    check = luhn_check_digit(partial)
    return partial + str(check)


def format_card(number: str) -> str:
    """Pretty-print card number in 4-digit groups."""
    groups = [number[i:i+4] for i in range(0, len(number), 4)]
    return ' '.join(groups)


# ──────────────────────────────────────────────
#  EXPIRY DATE GENERATION
# ──────────────────────────────────────────────

def future_expiry(years_ahead: int = 2) -> str:
    """Generate a future expiry date in MM/YY format."""
    future = datetime.now() + timedelta(days=365 * years_ahead + random.randint(1, 180))
    return future.strftime("%m/%y")


# ──────────────────────────────────────────────
#  CARD DEFINITIONS
# ──────────────────────────────────────────────

CARDS = [
    {
        "brand": "Visa",
        "label": "Visa Generic",
        "length": 16,
        "cvv_length": 3,
        "prefixes": ["4"],
        "static_bins": [
            "427082901528",  # User-provided first 12
        ],
        "auto_generate": False,  # Use static_bins only
    },
    {
        "brand": "Mastercard",
        "label": "Mastercard Generic",
        "length": 16,
        "cvv_length": 3,
        "prefixes": ["51", "52", "53", "54", "55", "2221", "2222", "2223",
                      "2230", "2231", "2232", "2233", "2234", "2235",
                      "2236", "2237", "2238", "2239", "2240", "2241",
                      "2300", "2301", "2302", "2303", "2304", "2305",
                      "2400", "2401", "2500", "2501", "2502", "2503",
                      "2600", "2601", "2602", "2603", "2604", "2605",
                      "2700", "2701", "2702", "2703", "2704", "2705",
                      "2710", "2711", "2712", "2713", "2714", "2715",
                      "2720"],
    },
    {
        "brand": "Discover",
        "label": "Discover Generic",
        "length": 16,
        "cvv_length": 3,
        "prefixes": ["6011", "622126", "622127", "622128", "622129",
                     "622130", "622131", "622132", "622133", "622134",
                     "622135", "622136", "622137", "622138", "622139",
                     "622140", "622141", "622142", "622143", "622144",
                     "622145", "622146", "622147", "622148", "622149",
                     "622150", "644", "645", "646", "647", "648", "649",
                     "65"],
    },
    {
        "brand": "American Express",
        "label": "Amex Delta SkyMiles",
        "length": 15,
        "cvv_length": 4,
        "prefixes": ["34", "37"],
        "static_bins": [
            "37976415610",  # User-provided first 11 (Delta)
            "37111643363",  # User-provided first 11 (Gold)
        ],
        "auto_generate": False,
    },
]


# ──────────────────────────────────────────────
#  CARD GENERATION ENGINE
# ──────────────────────────────────────────────

def generate_cards(count_per_type: int = 3) -> list:
    """Generate {count_per_type} cards per card definition."""
    results = []

    for card_def in CARDS:
        expiry = future_expiry()
        brand = card_def["brand"]
        label = card_def["label"]
        length = card_def["length"]
        cvv_len = card_def["cvv_length"]
        cvv = ''.join(str(random.randint(0, 9)) for _ in range(cvv_len))

        if not card_def.get("auto_generate", True) and card_def.get("static_bins"):
            # Use explicitly provided BIN prefixes
            for prefix in card_def["static_bins"]:
                number = generate_full_number(prefix, length)
                results.append({
                    "brand": brand,
                    "label": label,
                    "number": number,
                    "formatted": format_card(number),
                    "expiry": expiry,
                    "cvv": cvv,
                    "length": length,
                })
        else:
            # Auto-generate from prefix list
            for i in range(count_per_type):
                prefix = random.choice(card_def["prefixes"])
                # Expand short prefixes to reasonable account length
                if len(prefix) < 6:
                    expand_len = min(6, length - 2) - len(prefix)
                    if expand_len > 0:
                        prefix += ''.join(str(random.randint(0, 9)) for _ in range(expand_len))
                number = generate_full_number(prefix, length)
                results.append({
                    "brand": brand,
                    "label": label,
                    "number": number,
                    "formatted": format_card(number),
                    "expiry": expiry,
                    "cvv": cvv,
                    "length": length,
                })

    return results


# ──────────────────────────────────────────────
#  LUHN VALIDATION
# ──────────────────────────────────────────────

def luhn_validate(number: str) -> bool:
    """Verify a complete card number passes Luhn."""
    clean = number.replace(' ', '')
    if not clean.isdigit():
        return False
    return luhn_check_digit(clean[:-1]) == int(clean[-1])


# ──────────────────────────────────────────────
#  OUTPUT
# ──────────────────────────────────────────────

def print_results(cards: list):
    """Pretty-print all generated cards in a table."""
    print("=" * 80)
    print("  CARDGEN — Luhn-Valid Test Credit Card Generator")
    print("  For authorized penetration testing only")
    print("=" * 80)
    print()

    for c in cards:
        valid = "✓" if luhn_validate(c["number"]) else "✗"
        print(f"  [{c['brand']:18s}] {c['label']}")
        print(f"  {'':20s} {c['formatted']}")
        print(f"  {'':20s} Exp: {c['expiry']}  CVV/CID: {c['cvv']}")
        print(f"  {'':20s} Luhn: {valid}")
        print()

    print("-" * 80)
    print(f"  Total cards generated: {len(cards)}")
    print("  All numbers verified via Luhn algorithm.")
    print("=" * 80)


def print_json(cards: list):
    """Output cards as JSON (pipe to jq or redirect as needed)."""
    import json
    output = []
    for c in cards:
        output.append({
            "brand": c["brand"],
            "label": c["label"],
            "number": c["number"],
            "formatted": c["formatted"],
            "expiry": c["expiry"],
            "cvv": c["cvv"],
            "luhn_valid": luhn_validate(c["number"]),
        })
    print(json.dumps(output, indent=2))


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # Parse optional CLI args
    count = 3
    output_format = "table"

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--count="):
                count = int(arg.split("=")[1])
            elif arg == "--json":
                output_format = "json"
            elif arg in ("-h", "--help"):
                print("Usage: python3 cardgen.py [--count=N] [--json]")
                print("  --count=N   Cards per type (default: 3)")
                print("  --json      Output in JSON format")
                sys.exit(0)

    cards = generate_cards(count_per_type=count)

    if output_format == "json":
        print_json(cards)
    else:
        print_results(cards)
