import re

KEYWORD_CATEGORY_MAP = {
    "linux": "computers",
    "python": "programming",
    "java": "programming",
    "react": "programming",
    "kubernetes": "devops",
    "network": "networking",
    "tcp/ip": "networking",
    "tcp": "networking",
    " ip ": "networking",
    "hacking": "security",
    "hack": "security",
    "blockchain": "blockchain",
    "drawing": "art",
    "sketch": "art",
    "design": "design",
    "zoo": "zoology",
    "animal": "zoology",
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

    # Art / Drawing / Design
    "Loomis": "Art",
    "Bridgman": "Art",
    "Bargue": "Art",
    "Sketch": "Art",
    "Drawing": "Art",
    "Color and Light": "Art",
    "Illustration": "Art",
    "Art": "Art",
    "Subway Art": "Art",

    # Astronomy / Space
    "Astrobiology": "Astronomy",
    "Planet Formation": "Astronomy",
    "Astronomy": "Astronomy",
    "Telescope": "Astronomy",
    "Solar System": "Astronomy",
    "Curiosity": "Astronomy",

    # Biology / Botany / Zoology
    "Botanica": "Biology",
    "Árboles": "Biology",
    "Zoología": "Biology",
    "Species": "Biology",
    "Omega": "Biology",
    "Grzimek": "Biology",

    # Chemistry / Physics / General Science
    "Chemistry": "Science",
    "Química": "Science",
    "Physics": "Science",
    "Chemical": "Science",
    "Applied Numerical Analysis": "Science",
    "Fundamentals": "Science",

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
    "Data Mining": "Computer Science",
    "Software": "Computer Science",
    "Pressman": "Computer Science",
    "NODE_VOL": "Computer Science",

    # Cryptography / Security
    "Cryptography": "Security",
    "Cyber": "Security",
    "Blue Team": "Security",
    "Practical Cryptography": "Security",
    "Stuxnet": "Security",
    "Security": "Security",

    # DIY / Craft / Maker
    "Making Stuff": "DIY",
    "DIY": "DIY",
    "Folding Knives": "DIY",
    "Making": "DIY",
    "Do It Yourself": "DIY",

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
    "Kill or Get Killed": "Forensics",
    "Survival": "Forensics",
    "SAS": "Forensics",
    "Ballistics": "Forensics",

    # Military / Strategy
    "MCWP": "Military",
    "MCRP": "Military",
    "AFMAN": "Military",
    "Training": "Military",
    "Urbanized": "Military",
    "MOUT": "Military",
    "Military": "Military",
    "Weapons": "Military",
    "Fighter": "Military",
    "Raptor": "Military",

    # Business / Startup
    "Zero to One": "Business",
    "Startup": "Business",
    "Entrepreneur": "Business",
    "Business": "Business",

    # Anarchism / Counterculture
    "Steal This Book": "Anarchism",
    "Anarchist Cookbook": "Anarchism",
    "Abbie Hoffman": "Anarchism",
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
    "pentest+": "certification",
    "security+": "certification",
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

    # Data and machine learning
    "data analysis": "data",
    "data mining": "data",
    "data ethics": "data",
    "data": "data",
    "python for data analysis": "data",
    "machine learning": "data",
    "artificial intelligence": "data",

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

    # Fiction
    "dune": "fiction",
    "zafón": "fiction",
    "his dark materials": "fiction",
    "house of leaves": "fiction",
    "blood meridian": "fiction",
    "solarpunk": "fiction",
    "lord of the flies": "fiction",
    "master of djinn": "fiction",
    "tram car": "fiction",
    "harry quebert": "fiction",

    # Borges
    "libro de arena": "borges",

    # Game development
    "godot": "gamedev",
    "game engine": "gamedev",
    "game ai": "gamedev",
    "physically based rendering": "gamedev",

    # Design / Visualization / General
    "design elements": "art",
    "motel of the mysteries": "art",  # borderline satirical/art/design
    "paper airplane": "aero",

    # Misc
    "hardware hacking": "electronics",
    "energy": "engineering",


}


def category_fallback_obsolete(filename):
    categories = []

    if (
         "comp" in filename or
         " hack" in filename or
         " cyber" in filename or
         " vpn " in filename):
        categories.append("computers")

    if (
         "aero" in filename or
         " aircr" in filename or
         "flight" in filename):
        categories.append("aeronautics")

    if (
         "astron" in filename or
         ("star" in filename and "started" not in filename) or
         "galaxy" in filename or
         "planet" in filename or
         "moon" in filename
         ):
        categories.append("astronomy")

    if "phys" in filename or "fisica" in filename:
        categories.append("physics")

    if "animal" in filename:
        categories.append("zoology")

    if (
         "army" in filename or
         " war " in filename or
         " milit" in filename):
        categories.append("military")

    if "anatom" in filename:
        categories.append("anatomy")

    if (
         " anim" in filename or
         " draw" in filename or
         " paint" in filename):
        categories.append("art")

    if "german" in filename:
        categories.append("german")

    if (
         "game" in filename or
         "unity" in filename or
         "godot" in filename):
        categories.append("games")

    if (
         "training" in filename or
         "excercise" in filename or
         "martial" in filename):
        categories.append("training")

    if ("engineering" in filename):
        categories.append("engineering")

    return categories


def category_fallback(path: str) -> str:
    """
    Attempts to determine a category from the file path using keyword matching.
    Returns a standardized category or 'uncategorized' if no match is found.
    """
    path_tokens = re.findall(r"\w+", path.lower())

    categories = []
    for token in path_tokens:
        for keyword, category in KEYWORD_CATEGORY_MAP.items():
            if keyword in token:
                categories.append(category)

    if categories:
        return categories

    return ["uncategorized"]
