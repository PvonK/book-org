import re

# TODO Make categoty_fallback stricter
# and less prone to false positives

KEYWORD_CATEGORY_MAP = {
    "linux": "computers",
    "compu": "computers",
    "cyber": "computers",
    "vpn": "computers",

    "python": "programming",
    "java": "programming",
    "react": "programming",
    "kubernetes": "devops",
    "network": "networking",
    "tcp/ip": "networking",
    "tcp": "networking",
    " ip ": "networking",
    "hacking": "cybersecurity",
    "hack": "cybersecurity",
    "blockchain": "blockchain",
    "drawing": "art",
    "sketch": "art",
    "zoo": "zoology",
    "space": "astronomy",
    "game": "gamedev",
    "unity": "gamedev",

    # Aerospace / Aviation
    "F-22": "Aerospace",
    "F-104G": "Aerospace",
    "F-106": "Aerospace",
    "F18": "Aerospace",
    "NACA": "Aerospace",
    "Flight": "Aerospace",
    "aeromechanics": "Aerospace",
    "aircraft": "Aerospace",
    "aero": "Aerospace",
    "rotorcraft": "Aerospace",
    "observations of shock waves": "Aerospace",
    "aircr": "Aerospace",
    "flight": "Aerospace",

    # Art / Drawing / Design
    "Loomis": "Art",
    "Bridgman": "Art",
    "Bargue": "Art",
    "Sketch": "Art",
    "Drawing": "Art",
    "Color and Light": "Art",
    "Illustration": "Art",
    " Art": "Art",
    "Subway Art": "Art",

    # Astronomy / Space
    "Astrobiology": "Astronomy",
    "Planet Formation": "Astronomy",
    "Astronomy": "Astronomy",
    "Telescope": "Astronomy",
    "Solar System": "Astronomy",
    "Curiosity": "Astronomy",
    "astron": "Astronomy",
    "galaxy": "Astronomy",
    "planet": "Astronomy",
    "moon": "Astronomy",

    # Biology / Botany / Zoology
    "Botanica": "Biology",
    "Árboles": "Biology",
    "Zoología": "Biology",
    "Species": "Biology",
    "Omega": "Biology",
    "Grzimek": "Biology",
    "animal": "Biology",


    # Chemistry / Physics / General Science
    "Chemistry": "Science",
    "Química": "Science",
    "Physics": "Science",
    "Chemical": "Science",
    "Applied Numerical Analysis": "Science",
    "Fundamentals": "Science",
    "phys": "Science",

    # Chess
    "Chess": "Chess",
    "Caro-Kann": "Chess",
    "Sveshnikov": "Chess",
    "Endgame": "Chess",
    "Polgar": "Chess",
    "Gambit": "Chess",
    "Eade": "Chess",
    "Silman": "Chess",

    # Computing / CS / Networking
    "Computer Science": "Computer Science",
    "Networking": "Computer Science",
    "Stallings": "Computer Science",
    "Internetworking": "Computer Science",
    "Distributed": "Computer Science",
    "Cloud": "Computer Science",
    "API": "Computer Science",
    "Data": "Computer Science",
    "Software": "Computer Science",
    "Pressman": "Computer Science",
    "NODE_VOL": "Computer Science",

    # Cryptography / Security
    "Cryptography": "cybersecurity",
    "Cyber": "cybersecurity",
    "Practical Cryptography": "cybersecurity",
    "Stuxnet": "cybersecurity",
    "Security": "cybersecurity",

    # DIY / Craft / Maker
    "Making Stuff": "DIY",
    "DIY": "DIY",
    "Folding Knives": "DIY",
    "Making": "DIY",
    "Yourself": "DIY",

    # Fantasy / Sci-Fi / Fiction
    "Necronomicon": "Fiction",
    "Lovecraft": "Fiction",
    "D&D": "Fiction",
    "Dragons": "Fiction",
    "Cloud Atlas": "Fiction",
    "Hitchhiker": "Fiction",
    "Lupin": "Fiction",

    # Forensics / Criminology / Survival
    "Forensic": "Forensics",
    "Crime": "Forensics",
    "Criminology": "Forensics",
    "Investigator": "Forensics",
    "Survival": "Forensics",
    "SAS": "Forensics",
    "Ballistics": "Forensics",

    # Military / Strategy
    "MCWP": "Military",
    "MCRP": "Military",
    "AFMAN": "Military",
    "Urbanized": "Military",
    "MOUT": "Military",
    "Military": "Military",
    "Weapons": "Military",
    "Fighter": "Military",
    "Raptor": "Military",
    "army": "Military",
    "war": "Military",
    "milit": "Military",

    # Training
    "training": "training",
    "excercise": "training",
    "martial": "training",

    # Business / Startup
    "Startup": "Business",
    "Entrepreneur": "Business",
    "Business": "Business",

    # Anarchism / Counterculture
    "Steal": "Anarchism",
    "Anarch": "Anarchism",
    "Anarchist": "Anarchism",
    "Counterculture": "Anarchism",


    # Cryptography and blockchain
    "cryptography": "cybersecurity",
    "crypto": "cybersecurity",
    "bitcoin": "blockchain",
    "ethereum": "blockchain",
    "blockchain": "blockchain",
    "solidity": "blockchain",
    "smart contract": "blockchain",
    "mining": "blockchain",
    "opnsense": "cybersecurity",

    # Cybersecurity and certifications
    "penetration testing": "cybersecurity",
    "ethical hacker": "cybersecurity",
    "ceh": "certification",
    "crisc": "certification",
    "cka": "certification",
    "aws certified security": "certification",
    "comptia": "certification",
    "network+": "certification",
    "ccna": "certification",
    "cisco": "networking",
    "cybersecurity": "cybersecurity",
    "security": "cybersecurity",
    "risk": "cybersecurity",

    # Networking
    "network": "networking",
    "networking": "networking",

    # DevOps
    "devops": "devops",
    "gitlab": "devops",
    "ci/cd": "devops",

    # Aerospace and flight
    "x-15": "aerospace",
    "xb-70": "aerospace",
    "xp-51": "aerospace",
    "flight simulation": "aerospace",
    "aerospace": "aerospace",
    "drones": "aerospace",
    "uav": "aerospace",
    "spaceship": "aerospace",

    # Game development
    "godot": "gamedev",
    "rendering": "gamedev",
    "game": "gamedev",
    "unity": "gamedev",
    "godot": "gamedev",

    # Design / Visualization / General
    "design": "art",
    "paper airplane": "art",
    "anim": "art",
    "draw": "art",
    "paint": "art",

    # Misc
    "hardware hacking": "electronics",
    "energy": "engineering",
    "anatom": "anatomy",
    "german": "german",
    "engineering": "engineering",

}


def category_fallback(path: str) -> str:
    """
    Attempts to determine a category from the file path using keyword matching.
    Returns a standardized category or 'uncategorized' if no match is found.
    """
    path_tokens = re.findall(r"\w+", path.lower())

    categories = []
    print(path_tokens)
    for token in path_tokens:
        for keyword, category in KEYWORD_CATEGORY_MAP.items():
            if keyword.lower() in token.lower():
                categories.append(category)

    if categories:
        return list(set(categories))

    return []
