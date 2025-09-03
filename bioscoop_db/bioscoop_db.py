import sqlite3
import random
import unicodedata
import re
from faker import Faker
from datetime import datetime

aantal_bezoekers = 1000
aantal_tickets = 2000
aantal_personeel = 30
# Zoek naar `films_data` voor de films die in deze bios gedraaid worden. Leuk om te updaten naar nieuwe films :)

# Database-filename
database = "bioscoop.db"

faker = Faker("nl_NL")
used_names = set()


def clean_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()
    return re.sub(r'[^a-zA-Z ]', '', name)

def unique_name():
    while True:
        first = clean_name(faker.first_name())
        last = clean_name(faker.last_name())
        full = f"{first} {last}"
        if full not in used_names:
            used_names.add(full)
            return first, last

print("Script gestart.")

conn = sqlite3.connect(database)
cur = conn.cursor()

print(f"Verbonden met database {database}")

cur.executescript("""
DROP TABLE IF EXISTS bezoekers;
DROP TABLE IF EXISTS films;
DROP TABLE IF EXISTS vertoningen;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS personeel;
""")

print(f"{database} is gedropped.")

cur.executescript("""
CREATE TABLE bezoekers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voornaam TEXT,
    achternaam TEXT,
    leeftijd INTEGER
);

CREATE TABLE films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT,
    genre TEXT,
    minimale_leeftijd INTEGER
);

CREATE TABLE vertoningen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    film_id INTEGER,
    zaal INTEGER,
    datum TEXT
);

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bezoeker_id INTEGER,
    vertoning_id INTEGER,
    prijs REAL
);

CREATE TABLE personeel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voornaam TEXT,
    achternaam TEXT,
    functie TEXT,
    zaal INTEGER
);
""")

print(f"{database} is aangemaakt.")

for _ in range(aantal_bezoekers):
    first, last = unique_name()
    leeftijd = random.randint(8, 80)
    cur.execute("INSERT INTO bezoekers (voornaam, achternaam, leeftijd) VALUES (?, ?, ?)",
                (first, last, leeftijd))
    
print(f"{aantal_bezoekers} bezoekers zijn aangemaakt.")

films_data = [
    ("Lilo & Stitch", "Animatie", 6),
    ("Mission: Impossible – Final Reckoning", "Actie", 12),
    ("Ballerina - From the World of John Wick", "Actie", 16),
    ("Final Destination: Bloodlines", "Horror", 16),
    ("The Phoenician Scheme", "Thriller", 16)
]
for titel, genre, min_leeftijd in films_data:
    cur.execute("INSERT INTO films (titel, genre, minimale_leeftijd) VALUES (?, ?, ?)",
                (titel, genre, min_leeftijd))

print("Films zijn aangemaakt.")


for film_id in range(1, len(films_data) + 1):
    for _ in range(10):
        zaal = random.randint(1, 5)
        dt = faker.date_time_this_month()
        datum = dt.strftime("%d/%m/%Y %H:%M")
        cur.execute("INSERT INTO vertoningen (film_id, zaal, datum) VALUES (?, ?, ?)",
                    (film_id, zaal, datum))

cur.execute("SELECT MAX(id) FROM vertoningen")
max_vert_id = cur.fetchone()[0]

for _ in range(aantal_tickets):
    bezoeker_id = random.randint(1, aantal_bezoekers)
    vertoning_id = random.randint(1, max_vert_id)
    prijs = random.choice([8.50, 10.00, 11.50])
    cur.execute(
        "INSERT INTO tickets (bezoeker_id, vertoning_id, prijs) VALUES (?, ?, ?)",
        (bezoeker_id, vertoning_id, prijs)
    )

print(f"{aantal_tickets} tickets zijn aangemaakt.")

functies = ["Projectie", "Schoonmaak", "Kaartcontrole", "Snackbalie", "Schoonmaak", "Projectie"]
for _ in range(aantal_personeel):
    first, last = unique_name()
    naam = f"{first} {last}"
    functie = random.choice(functies)

    # Alleen Projectie en Schoonmaak hebben een zaalnummer
    if functie in ["Projectie", "Schoonmaak"]:
        zaal = random.randint(1, 5)
    else:
        zaal = None

    cur.execute(
        "INSERT INTO personeel (voornaam, achternaam, functie, zaal) VALUES (?, ?, ?, ?)",
        (first, last, functie, zaal)
    )

print(f"{aantal_personeel} personeel zijn aangemaakt.")

conn.commit()
conn.close()