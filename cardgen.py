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
# These three functions handle all Luhn math. The core insight:
# Given N-1 known digits, we can always compute the Nth (check) digit
# that makes the whole PAN pass Luhn validation.

def luhn_checksum(pan: str) -> int:
    """
    Compute the Luhn checksum for a PAN string.

    How it works step by step:
    1. Strip out any non-digit characters (spaces, dashes, etc.)
    2. Convert each character to an integer
    3. Process digits from RIGHT to LEFT (this is critical)
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
    # Step 1: Remove anything that isn't a digit (spaces, hyphens, etc.)
    digits = [int(d) for d in pan if d.isdigit()]

    total = 0

    # Step 2-6: Process from rightmost digit (index 0 after reversal)
    # enumerate(reversed) gives us (position_from_right, digit_value)
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:  # Every SECOND digit from the right gets doubled
            d *= 2
            if d > 9:    # If doubling gives 10+, subtract 9 (same as summing digits)
                d -= 9
        total += d       # Add to running total

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
    # Calculate total as if check digit were 0
    total = luhn_checksum(partial + "0")

    # What digit do we need to add to make total divisible by 10?
    # If total % 10 = 3, we need 7 (since 10 - 3 = 7)
    # If total % 10 = 0, we need 0 (since (10 - 0) % 10 = 0)
    check_digit = (10 - (total % 10)) % 10

    return check_digit


def is_valid_luhn(pan: str) -> bool:
    """
    Verify that a complete PAN passes Luhn validation.
    Returns True if the PAN is valid, False otherwise.

    This is the same algorithm used by POS systems to do a basic
    sanity check on card numbers before processing.
    """
    return luhn_checksum(pan) % 10 == 0


# =============================================================================
# SECTION 2: CARD BRAND CONFIGURATION
# =============================================================================
# This dictionary stores YOUR specific BINs and partial account numbers.
#
# Two types of entries:
#   "partials" - You have a partial PAN with some digits already known.
#                The program fills the remaining unknown positions.
#                Example: "37976415610" is 11 out of 15 Amex digits.
#
#   "bins" - You only have the BIN (first 6ish digits).
#            The program generates everything after the BIN randomly.
#            Example: "6011" is just the BIN prefix for Discover.

BRANDS = {
    # -- VISA -----------------------------------------------------------------
    # Your Visa partial: 427082901528 (12 digits)
    # Visa is 16 digits total, so we need 3 random filler + 1 check digit = 4 more
    "1": {
        "name": "Visa",
        "partials": [
            "427082901528",  # 12 known digits -> needs 3 filler + 1 check
        ],
        "length": 16,  # Standard Visa length
    },

    # -- MASTERCARD -----------------------------------------------------------
    # Your Mastercard partial: 521333124685 (12 digits)
    # Mastercard is 16 digits total, so we need 3 random filler + 1 check digit = 4 more
    "2": {
        "name": "Mastercard",
        "partials": [
            "521333124685",  # 12 known digits -> needs 3 filler + 1 check
        ],
        "length": 16,  # Standard Mastercard length
    },

    # -- AMERICAN EXPRESS -----------------------------------------------------
    # Amex is 15 digits total.
    # Your partials are 11 digits each -> needs 3 random filler + 1 check = 4 more
    "3": {
        "name": "American Express",
        "partials": [
            "37976415610",    # 11 known digits (Delta SkyMiles) -> 3 filler + 1 check
            "37111643363",    # 11 known digits (Gold) -> 3 filler + 1 check
            "34120302757",    # 11 known digits (Cash Preferred) -> 3 filler + 1 check
        ],
        "length": 15,  # Amex is always 15 digits
    },

    # -- DISCOVER -------------------------------------------------------------
    # For Discover you only provided BINs (not partial account numbers).
    # The program picks a random BIN, then generates the remaining digits.
    #
    # BIN length varies:
    #   "6011" is 4 digits -> needs 11 random filler + 1 check = 12 more
    #   "622126" is 6 digits -> needs 9 random filler + 1 check = 10 more
    #   "644" is 3 digits -> needs 12 random filler + 1 check = 13 more
    #   "65" is 2 digits -> needs 13 random filler + 1 check = 14 more
    #
    # The generate_pan_from_partial function handles this automatically
    # by calculating: target_length - 1 - len(bin) = filler digits needed
    "4": {
        "name": "Discover",
        "bins": [
            # Standard Discover BINs:
            "6011",

            # Discover 622126-622150 range (6-digit BINs):
            "622126", "622127", "622128", "622129",
            "622130", "622131", "622132", "622133", "622134",
            "622135", "622136", "622137", "622138", "622139",
            "622140", "622141", "622142", "622143", "622144",
            "622145", "622146", "622147", "622148", "622149",
            "622150",

            # Discover 644-649 range (3-digit BINs):
            "644", "645", "646", "647", "648", "649",

            # Discover 65 prefix (2-digit BIN):
            "65",
        ],
        "length": 16,  # Standard Discover length
    },
}


# =============================================================================
# SECTION 3: PAN GENERATION LOGIC
# =============================================================================

def generate_pan_from_partial(partial: str, target_length: int) -> str:
    """
    GENERATE A SINGLE VALID PAN FROM A PARTIAL.

    This is the core function. Here's the complete flow:

    Example with Amex partial "37976415610" (target length 15):

    Step 1: Clean input -> "37976415610" (already clean)
    Step 2: Calculate filler needed:
             target_length - 1 - len(clean) = 15 - 1 - 11 = 3
             We need 3 random filler digits before the check digit.
    Step 3: Generate random filler -> e.g., "847"
    Step 4: Construct PAN without check digit:
             "37976415610" + "847" = "37976415610847"
    Step 5: Calculate Luhn check digit for this string -> e.g., 3
    Step 6: Full PAN = "37976415610847" + "3" = "379764156108473"
    Step 7: Validate that it passes Luhn (assertion check)

    Args:
        partial: Known digits of the PAN (BIN + any fixed account digits)
        target_length: Full PAN length (16 for Visa/MC/Discover, 15 for Amex)

    Returns:
        Complete PAN string of length `target_length` that passes Luhn

    Raises:
        ValueError: If the partial is longer than the target PAN
    """
    # Step 1: Strip any non-digit characters just in case
    clean = "".join(c for c in partial if c.isdigit())

    # Step 2: Calculate how many random filler digits we need
    # Formula: target_length - 1 (for check digit) - len(known_partial)
    # If this is negative, the partial is already too long for this card type
    filler_count = target_length - 1 - len(clean)

    if filler_count < 0:
        raise ValueError(
            f"Partial too long ({len(clean)} digits) for "
            f"{target_length}-digit PAN"
        )

    # Step 3: Generate random filler digits
    # Each digit is 0-9, chosen uniformly at random
    filler = "".join(str(random.randint(0, 9)) for _ in range(filler_count))

    # Step 4: Build the PAN without the check digit
    # This is: known_partial + random_filler
    pan_no_check = clean + filler

    # Step 5: Calculate the correct Luhn check digit for this string
    check_digit = calculate_check_digit(pan_no_check)

    # Step 6: Append the check digit to get the full PAN
    full_pan = pan_no_check + str(check_digit)

    # Step 7: Sanity check - verify the PAN we just built passes Luhn
    # This assertion will fail if there's a bug in calculate_check_digit
    assert is_valid_luhn(full_pan), (
        f"Generated PAN failed Luhn validation: {full_pan}"
    )
    assert len(full_pan) == target_length, (
        f"Generated PAN length {len(full_pan)} != expected {target_length}"
    )

    return full_pan


def generate_pans(brand_key: str, count: int = 50) -> list:
    """
    GENERATE MULTIPLE PANs FOR A GIVEN BRAND.

    For each PAN to generate:
    1. Pick a random entry from the brand's partials or bins list
    2. Feed it to generate_pan_from_partial with the correct target length
    3. Collect all results

    Args:
        brand_key: String key into the BRANDS dictionary ("1", "2", "3", or "4")
        count: How many PANs to generate (default 50)

    Returns:
        List of valid PAN strings
    """
    config = BRANDS[brand_key]
    pans = []

    for _ in range(count):
        # Check if this brand uses "partials" (known account digits)
        # or "bins" (just the BIN prefix, rest is random)
        if "partials" in config:
            # Pick one of the user's partial PANs at random
            partial = random.choice(config["partials"])
            pan = generate_pan_from_partial(partial, config["length"])

        elif "bins" in config:
            # Pick one of the user's BINs at random
            bin_str = random.choice(config["bins"])
            pan = generate_pan_from_partial(bin_str, config["length"])

        else:
            # This should never happen if the config is set up correctly
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

    Flow:
    1. Print welcome banner
    2. Show menu with card brands
    3. User selects a brand (or exits)
    4. Generate 50 PANs and display them
    5. Show Luhn validation status
    6. Loop back to menu
    """
    print("=" * 75)
    print("  PAN Generator - Authorized Penetration Testing")
    print("=" * 75)
    print("  Calculates missing digits + Luhn check digit")
    print("  from your known BINs and partial account numbers.")
    print("  Every generated PAN passes Luhn validation.")
    print("=" * 75)

    # Main loop: keep showing the menu until the user exits
    while True:
        # -- Display menu ----------------------------------------------------
        print("\nCard brands:")
        for key, config in BRANDS.items():
            # Determine whether this brand uses partials or BINs
            source = "partials" if "partials" in config else "BINs"
            count = len(config.get("partials", config.get("bins", [])))
            print(f"  {key}. {config['name']} ({config['length']} digits, {count} {source})")
        print("  0. Exit")

        # -- Get user input --------------------------------------------------
        choice = input("\nSelect brand: ").strip()

        # -- Handle exit ----------------------------------------------------
        if choice == "0":
            print("Exiting.")
            break

        # -- Validate choice ------------------------------------------------
        if choice not in BRANDS:
            print("Invalid selection. Try again.")
            continue

        # -- Generate and display PANs --------------------------------------
        brand_name = BRANDS[choice]["name"]

        print(f"\nGenerating 50 {brand_name} PANs...\n")

        # Generate 50 PANs for the selected brand
        pans = generate_pans(choice, count=50)

        # Print each PAN on its own line, numbered 1-50
        for i, pan in enumerate(pans, 1):
            print(f"  {pan}")

        # -- Verify and report ----------------------------------------------
        # Check that ALL generated PANs pass Luhn validation
        all_valid = all(is_valid_luhn(p) for p in pans)
        status = "ALL PASS" if all_valid else "SOME FAILED"
        print(f"\n  Generated {len(pans)} {brand_name} PANs -- Luhn: {status}")


# =============================================================================
# SECTION 5: ENTRY POINT
# =============================================================================
# This block ensures the program only runs when executed directly
# (not when imported as a module by another script).

if __name__ == "__main__":
    main()
