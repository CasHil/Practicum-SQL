import sqlite3
import random
import unicodedata
import re
from faker import Faker

aantal_bezoekers = 500
aantal_tickets = 2000
aantal_personeel = 30

faker = Faker()
used_names = set()

def clean(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()
    name = re.sub(r'[^a-zA-Z]', '', name)
    return name

def generate_unique_name():
    while True:
        first = clean(faker.first_name())
        last = clean(faker.last_name())
        full = f"{first} {last}"
        if full not in used_names:
            used_names.add(full)
            return first, last

conn = sqlite3.connect("pretpark.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS Bezoekers;
DROP TABLE IF EXISTS Attracties;
DROP TABLE IF EXISTS Ritten;
DROP TABLE IF EXISTS Medewerkers;
DROP TABLE IF EXISTS Onderhoud;
""")

cur.executescript("""
CREATE TABLE bezoekers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voornaam TEXT,
    achternaam TEXT,
    leeftijd INTEGER
);

CREATE TABLE attracties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT,
    minimum_lengte INTEGER
);

CREATE TABLE ritten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bezoeker_id INTEGER,
    attractie_id INTEGER,
    tijdstip TEXT
);

CREATE TABLE medewerkers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT,
    attractie_id INTEGER
);

CREATE TABLE onderhoud (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attractie_id INTEGER,
    type TEXT,
    datum TEXT
);
""")

for _ in range(500):
    voornaam, achternaam = generate_unique_name()
    leeftijd = random.randint(6, 70)
    cur.execute("INSERT INTO bezoekers (voornaam, achternaam, leeftijd) VALUES (?, ?, ?)",
                (voornaam, achternaam, leeftijd))

attracties = [
    ("Kikkerbaan", 90),
    ("Draaimolen", 0),
    ("Achtbaan", 120),
    ("Spookhuis", 100),
    ("Reuzenrad", 0)
]
for naam, min_lengte in attracties:
    cur.execute("INSERT INTO attracties (naam, minimum_lengte) VALUES (?, ?)", (naam, min_lengte))

for _ in range(2000):
    bezoeker_id = random.randint(1, 500)
    attractie_id = random.randint(1, len(attracties))
    tijdstip = faker.date_time_this_year().isoformat()
    cur.execute("INSERT INTO Ritten (bezoeker_id, attractie_id, tijdstip) VALUES (?, ?, ?)",
                (bezoeker_id, attractie_id, tijdstip))

# Voeg Medewerkers toe (inclusief 'Abel Berends') voor opdrachten over databases
cur.execute("INSERT INTO medewerkers (naam, attractie_id) VALUES (?, ?)",
            ("Abel Berends", 3))

for _ in range(20):
    voornaam, achternaam = generate_unique_name()
    naam = f"{voornaam} {achternaam}"
    attractie_id = random.randint(1, len(attracties))
    cur.execute("INSERT INTO medewerkers (naam, attractie_id) VALUES (?, ?)", (naam, attractie_id))

types = ['veiligheidscheck', 'smeren', 'inspectie']
for _ in range(200):
    attractie_id = random.randint(1, len(attracties))
    onderhoudstype = random.choice(types)
    datum = faker.date_this_year().isoformat()
    cur.execute("INSERT INTO onderhoud (attractie_id, type, datum) VALUES (?, ?, ?)",
                (attractie_id, onderhoudstype, datum))

conn.commit()
conn.close()
print("Database 'pretpark.db' is aangemaakt.")
