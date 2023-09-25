import sqlite3
import random

# Sample data
name_list = ["john smith", "anne marrie", "michale williams"]
ssn_list = ["6374", "8542", "7456"]
county_list = [
    "alameda",
    "alpine",
    "amador",
    "butte",
    "calaveras",
    "colusa",
    "contra costa",
    "del norte",
    "el dorado",
    "fresno",
    "glenn",
    "humboldt",
    "imperial",
    "inyo",
    "kern",
    "kings",
    "lake",
    "lassen",
    "los angeles",
    "madera",
    "marin",
    "mariposa",
    "mendocino",
    "merced",
    "modoc",
    "mono",
    "monterey",
    "napa",
    "nevada",
    "orange",
    "placer",
    "plumas",
    "riverside",
    "sacramento",
    "san benito",
    "san bernardino",
    "san diego",
    "san francisco",
    "san joaquin",
    "san luis obispo",
    "san mateo",
    "santa barbara",
    "santa clara",
    "santa cruz",
    "shasta",
    "sierra",
    "siskiyou",
    "solano",
    "sonoma",
    "stanislaus",
    "sutter",
    "tehama",
    "trinity",
    "tulare",
    "tuolumne",
    "ventura",
    "yolo",
    "yuba",
]

# Open a connection to the database (creates a new DB if not exists)
conn = sqlite3.connect("user_database.db")
cursor = conn.cursor()

# Create the "user" table if not exists
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        user_type TEXT,
        provider_number TEXT,
        ssn TEXT,
        full_name TEXT,
        county TEXT
    )
"""
)

# Insert records
n = 10  # Number of records to insert
for _ in range(n):
    user_type = random.choice(["Provider"])
    provider_number = str(random.randint(100000000, 999999999))
    ssn = random.choice(ssn_list)
    full_name = random.choice(name_list)
    county = random.choice(county_list)

    # Insert data into the table
    cursor.execute(
        """
        INSERT INTO user (user_type, provider_number, ssn, full_name, county)
        VALUES (?, ?, ?, ?, ?)
    """,
        (user_type, provider_number, ssn, full_name, county),
    )

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"{n} records inserted successfully.")
