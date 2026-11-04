"""
compatibility.py - Blood group compatibility logic for HemoMatch
Phase 2 biology-based rules & evaluation functions.
"""

# Dictionary storing compatible recipient groups for each donor blood group
BLOOD_COMPATIBILITY = {
    "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],  # Universal donor
    "O+":  ["O+", "A+", "B+", "AB+"],
    "A-":  ["A-", "A+", "AB-", "AB+"],
    "A+":  ["A+", "AB+"],
    "B-":  ["B-", "B+", "AB-", "AB+"],
    "B+":  ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"]                                              # Universal recipient only
}


def normalize_blood_group(group: str) -> str:
    """
    Standardize blood group string:
    - Trims whitespace
    - Converts to uppercase
    - Converts various Unicode minus/dash characters to standard ASCII '-'
    """
    if not group:
        return ""
    text = str(group).strip().upper()
    for dash in ("\u2212", "\u2013", "\u2014", "\uff0d", "\u2010", "\u2011", "\u2012"):
        text = text.replace(dash, "-")
    return text


def check_blood_compatibility(donor: str, recipient: str) -> dict:
    """
    Compare donor and recipient blood groups according to biological rules.
    Returns a dictionary containing:
      - compatible (bool): True if safe to transfuse, False otherwise
      - status (str): 'compatible', 'incompatible', or 'warning'
      - title (str): Short summary status
      - message (str): Detailed medical compatibility explanation
      - donor (str): Normalized donor blood group
      - recipient (str): Normalized recipient blood group
    """
    donor_clean = normalize_blood_group(donor)
    recipient_clean = normalize_blood_group(recipient)

    # Validate that both donor and recipient are provided
    if not donor_clean or not recipient_clean:
        return {
            "compatible": False,
            "status": "warning",
            "title": "Selection Incomplete",
            "message": "Please choose both a donor and a recipient blood group.",
            "donor": donor_clean,
            "recipient": recipient_clean
        }

    # Validate donor group exists in dictionary
    if donor_clean not in BLOOD_COMPATIBILITY:
        return {
            "compatible": False,
            "status": "incompatible",
            "title": "Invalid Donor Group",
            "message": f"'{donor}' is not a recognized blood group.",
            "donor": donor_clean,
            "recipient": recipient_clean
        }

    # Retrieve compatible recipients for the donor
    compatible_recipients = BLOOD_COMPATIBILITY[donor_clean]
    is_compatible = recipient_clean in compatible_recipients

    if is_compatible:
        return {
            "compatible": True,
            "status": "compatible",
            "title": "Compatible Match!",
            "message": f"Donor {donor_clean} blood can safely be transfused to recipient {recipient_clean}.",
            "donor": donor_clean,
            "recipient": recipient_clean
        }
    else:
        return {
            "compatible": False,
            "status": "incompatible",
            "title": "Not Compatible",
            "message": f"Donor {donor_clean} red blood cells cannot be safely given to recipient {recipient_clean}.",
            "donor": donor_clean,
            "recipient": recipient_clean
        }
