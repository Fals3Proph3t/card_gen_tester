#!/usr/bin/env python3
"""
PAN Generator — Authorized Penetration Testing
==============================================
Calculates missing digits + Luhn check digit from known partial PANs and BINs.

HOW IT WORKS:
- You provide known digits from a card (BIN + partial account number)
- The program fills the unknown positions with random digits
- It calculates the correct Luhn check digit for the final position
- Every generated PAN passes standard Luhn validation (what POS systems use)

CARD BRANDS SUPPORTED:
  Visa (16 digits)       — uses your partial account number
  Mastercard (16 digits)  — uses your partial account number
  American Express (15)   — uses your partial account numbers
  Discover (16 digits)    — uses your BINs, generates remainder randomly

LUHN ALGORITHM EXPLANATION:
  The Luhn algorithm (mod 10) is a simple checksum used by all major card
  networks. It works by:
  1. Starting from the rightmost digit, double every second digit
  2. If doubling produces a two-digit number, sum those digits (or subtract 9)
  3. Sum all digits (both doubled and undoubled)
  4. The total must be divisible by 10 for the PAN to be valid
  5. The last digit of the PAN is the "check digit" chosen to make step 4 pass
"""

import random
import sys

# =============================================================================
# SECTION 1: LUHN ALGORITHM FUNCTIONS
# =============================================================================

def luhn_checksum(pan: str) -> int:
    """
    Compute the Luhn checksum for a PAN string.

    Steps:
    1. Strip out any non-digit characters (spaces, dashes, etc.)
    2. Convert each character to an integer
    3. Process digits from RIGHT to LEFT
    4. Double every second digit (positions 2, 4, 6... from the right)
    5. If a doubled digit is >= 10, subtract 9 (e.g., 7*2=14 -> 14-9=5)
    6. Sum everything
    7. Return the total

    A valid PAN will have a total divisible by 10 (total % 10 == 0).

    Args:
        pan: A string of digits (may include spaces/dashes)

    Returns:
        Integer sum of the Luhn-weighted digits
    """
    digits = [int(d) for d in pan if d.isdigit()]
    total = 0

    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d

    return total


def calculate_check_digit(partial: str) -> int:
    """
    Given a partial PAN WITHOUT its check digit, calculate what the
    check digit should be to make the whole PAN pass Luhn.

    The math:
    - Luhn checksum of (partial + "0") gives us a starting total
    - We need (total + X) % 10 == 0, where X is the check digit
    - Solving for X: X = (10 - total % 10) % 10
    - The % 10 at the end handles the edge case where total % 10 == 0

    Args:
        partial: All digits of the PAN EXCEPT the last (check) digit

    Returns:
        A single integer (0-9) that is the correct Luhn check digit
    """
    total = luhn_checksum(partial + "0")
    check_digit = (10 - (total % 10)) % 10
    return check_digit


def is_valid_luhn(pan: str) -> bool:
    """
    Verify that a complete PAN passes Luhn validation.
    Returns True if the PAN is valid, False otherwise.
    """
    return luhn_checksum(pan) % 10 == 0


# =============================================================================
# SECTION 2: CARD BRAND CONFIGURATION
# =============================================================================
# Edit this section to add your own BINs and partial account numbers.
#
# "partials" — You have a partial PAN with some digits already known.
#              The program fills the remaining unknown positions.
#
# "bins" — You only have the BIN (first few digits).
#          The program generates everything after the BIN randomly.

BRANDS = {
    # -- VISA -----------------------------------------------------------------
    "1": {
        "name": "Visa",
        "partials": [
            "427082901528",  # 12 known digits -> needs 3 filler + 1 check
        ],
        "length": 16,
    },

    # -- MASTERCARD -----------------------------------------------------------
    "2": {
        "name": "Mastercard",
        "partials": [
            "521333124685",  # 12 known digits -> needs 3 filler + 1 check
        ],
        "length": 16,
    },

    # -- AMERICAN EXPRESS -----------------------------------------------------
    "3": {
        "name": "American Express",
        "partials": [
            "37976415610",    # 11 known digits (Delta SkyMiles)
            "37111643363",    # 11 known digits (Gold)
            "34120302757",    # 11 known digits (Cash Preferred)
        ],
        "length": 15,  # Amex is always 15 digits
    },

    # -- DISCOVER -------------------------------------------------------------
    "4": {
        "name": "Discover",
        "bins": [
            "6011",
            "622126", "622127", "622128", "622129",
            "622130", "622131", "622132", "622133", "622134",
            "622135", "622136", "622137", "622138", "622139",
            "622140", "622141", "622142", "622143", "622144",
            "622145", "622146", "622147", "622148", "622149",
            "622150",
            "644", "645", "646", "647", "648", "649",
            "65",
        ],
        "length": 16,
    },
}


# =============================================================================
# SECTION 3: PAN GENERATION LOGIC
# =============================================================================

def generate_pan_from_partial(partial: str, target_length: int) -> str:
    """
    Generate a single Luhn-valid PAN from a partial number.

    Example with Amex partial "37976415610" (target length 15):
    - filler_count = 15 - 1 - 11 = 3 random digits
    - pan_no_check = "37976415610" + "847" = "37976415610847"
    - check_digit = calculate_check_digit("37976415610847") = 3
    - full_pan = "379764156108473"

    Args:
        partial: Known digits of the PAN (BIN + any fixed account digits)
        target_length: Full PAN length (16 for Visa/MC/Discover, 15 for Amex)

    Returns:
        Complete PAN string of length `target_length` that passes Luhn

    Raises:
        ValueError: If the partial is longer than the target PAN
    """
    clean = "".join(c for c in partial if c.isdigit())
    filler_count = target_length - 1 - len(clean)

    if filler_count < 0:
        raise ValueError(
            f"Partial too long ({len(clean)} digits) for "
            f"{target_length}-digit PAN"
        )

    filler = "".join(str(random.randint(0, 9)) for _ in range(filler_count))
    pan_no_check = clean + filler
    check_digit = calculate_check_digit(pan_no_check)
    full_pan = pan_no_check + str(check_digit)

    assert is_valid_luhn(full_pan), f"Generated PAN failed Luhn: {full_pan}"
    assert len(full_pan) == target_length, (
        f"Generated PAN length {len(full_pan)} != expected {target_length}"
    )

    return full_pan


def generate_pans(brand_key: str, count: int = 50) -> list:
    """
    Generate multiple PANs for a given brand.

    Args:
        brand_key: String key into the BRANDS dictionary ("1", "2", "3", "4")
        count: How many PANs to generate (default 50)

    Returns:
        List of valid PAN strings
    """
    config = BRANDS[brand_key]
    pans = []

    for _ in range(count):
        if "partials" in config:
            partial = random.choice(config["partials"])
            pan = generate_pan_from_partial(partial, config["length"])
        elif "bins" in config:
            bin_str = random.choice(config["bins"])
            pan = generate_pan_from_partial(bin_str, config["length"])
        else:
            raise ValueError(f"No partials or bins defined for {config['name']}")

        pans.append(pan)

    return pans


# =============================================================================
# SECTION 4: USER INTERFACE
# =============================================================================

def main():
    """
    Interactive menu that lets the user select a card brand and
    generates 50 valid PANs for that brand.
    """
    print("=" * 75)
    print("  PAN Generator - Authorized Penetration Testing")
    print("=" * 75)
    print("  Calculates missing digits + Luhn check digit")
    print("  from your known BINs and partial account numbers.")
    print("  Every generated PAN passes Luhn validation.")
    print("=" * 75)

    while True:
        print("\nCard brands:")
        for key, config in BRANDS.items():
            source = "partials" if "partials" in config else "BINs"
            count = len(config.get("partials", config.get("bins", [])))
            print(f"  {key}. {config['name']} ({config['length']} digits, {count} {source})")
        print("  0. Exit")

        choice = input("\nSelect brand: ").strip()

        if choice == "0":
            print("Exiting.")
            break

        if choice not in BRANDS:
            print("Invalid selection. Try again.")
            continue

        brand_name = BRANDS[choice]["name"]
        print(f"\nGenerating 50 {brand_name} PANs...\n")

        pans = generate_pans(choice, count=50)

        for i, pan in enumerate(pans, 1):
            print(f"  {pan}")

        all_valid = all(is_valid_luhn(p) for p in pans)
        status = "ALL PASS" if all_valid else "SOME FAILED"
        print(f"\n  Generated {len(pans)} {brand_name} PANs -- Luhn: {status}")


# =============================================================================
# SECTION 5: ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
