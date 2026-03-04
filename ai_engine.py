def score_case(accident_type, injury_description, liability):
    score = 0

    # Accident type scoring
    if "car" in accident_type.lower():
        score += 30
    elif "truck" in accident_type.lower():
        score += 35
    else:
        score += 15

    # Injury severity scoring
    if "surgery" in injury_description.lower():
        score += 40
    elif "hospital" in injury_description.lower():
        score += 25
    else:
        score += 10

    # Liability clarity scoring
    if "red light" in liability.lower() or "fault" in liability.lower():
        score += 30
    else:
        score += 10

    # Determine strength
    if score >= 80:
        strength = "Strong"
    elif score >= 50:
        strength = "Medium"
    else:
        strength = "Weak"

    summary = f"""
    Case Summary:
    Accident Type: {accident_type}
    Injury: {injury_description}
    Liability: {liability}

    Total Score: {score}
    Case Strength: {strength}
    """

    return score, strength, summary
