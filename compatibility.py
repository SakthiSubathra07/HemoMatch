
"""
compatibility.py - Blood group compatibility logic for HemoMatch
Phase 2 biology-based rules & evaluation functions.
"""

# Compatible recipient groups for each donor blood group
BLOOD_COMPATIBILITY = {
    "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+":  ["O+", "A+", "B+", "AB+"],
    "A-":  ["A-", "A+", "AB-", "AB+"],
    "A+":  ["A+", "AB+"],
    "B-":  ["B-", "B+", "AB-", "AB+"],
    "B+":  ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"]
}


def normalize_blood_group(group: str) -> str:
    """Normalize blood group input."""

    if not group:
        return ""

    text = str(group).strip().upper()

    for dash in ("\u2212", "\u2013", "\u2014", "\uff0d",
                 "\u2010", "\u2011", "\u2012"):
        text = text.replace(dash, "-")

    return text


def check_blood_compatibility(donor: str, recipient: str) -> dict:
    """Check donor and recipient blood group compatibility."""

    donor_clean = normalize_blood_group(donor)
    recipient_clean = normalize_blood_group(recipient)

    # Validate input
    if not donor_clean or not recipient_clean:
        return {
            "compatible": False,
            "status": "warning",
            "title": "Selection Incomplete",
            "message": "Please choose both a donor and a recipient blood group.",
            "donor": donor_clean,
            "recipient": recipient_clean
        }

    # Validate donor blood group
    if donor_clean not in BLOOD_COMPATIBILITY:
        return {
            "compatible": False,
            "status": "warning",
            "title": "Invalid Donor Group",
            "message": f"'{donor}' is not a recognized blood group.",
            "donor": donor_clean,
            "recipient": recipient_clean
        }

    # Validate recipient blood group
    if recipient_clean not in BLOOD_COMPATIBILITY:
        return {
            "compatible": False,
            "status": "warning",
            "title": "Invalid Recipient Group",
            "message": f"'{recipient}' is not a recognized blood group.",
            "donor": donor_clean,
            "recipient": recipient_clean
        }

    # Check compatibility
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

    return {
        "compatible": False,
        "status": "incompatible",
        "title": "Not Compatible",
        "message": f"Donor {donor_clean} red blood cells cannot be safely given to recipient {recipient_clean}.",
        "donor": donor_clean,
        "recipient": recipient_clean
    }
