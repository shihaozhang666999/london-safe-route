def get_crime_weights():
    """
    Returns a dictionary of crime type weights used for calculating safety scores.
    10 means most dangerous, 1 means safest.
    """
    return {
        "Violence and sexual offences": 5.0,
        "Robbery": 4.5,
        "Possession of weapons": 4.2,
        "Theft from the person": 4.0,
        "Criminal damage and arson": 3.5,
        "Burglary": 3.3,
        "Vehicle crime": 3.0,
        "Drugs": 2.8,
        "Other crime": 2.5,
        "Public order": 2.2,
        "Anti-social behaviour": 2.0,
        "Other theft": 2.0,
        "Shoplifting": 1.5,
        "Bicycle theft": 1.2,
    }
