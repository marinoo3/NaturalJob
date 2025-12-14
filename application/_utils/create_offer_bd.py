import sqlite3

connection = sqlite3.connect("offer.db")
connection.execute("PRAGMA foreign_keys = ON;")
cursor = connection.cursor()

schema_statements = [
    """
    CREATE TABLE IF NOT EXISTS COMPANY (
        company_id   INTEGER PRIMARY KEY,
        name         TEXT NOT NULL,
        description  TEXT,
        industry     TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS REGION (
        region_id INTEGER PRIMARY KEY,
        code      TEXT NOT NULL,
        name      TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS CITY (
        city_id   INTEGER PRIMARY KEY,
        name      TEXT NOT NULL,
        region_id INTEGER NOT NULL,
        FOREIGN KEY (region_id) REFERENCES REGION(region_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DESCRIPTION (
        description_id    INTEGER PRIMARY KEY,
        offer_description TEXT NOT NULL,
        profile_description TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS OFFER (
        offer_id       INTEGER PRIMARY KEY,
        title          TEXT NOT NULL,
        job_name       TEXT,
        job_type       TEXT,
        contract_type  TEXT,
        salary         TEXT,
        min_experience TEXT,
        latitude       REAL,
        longitude      REAL,
        date           TEXT,
        source         TEXT NOT NULL,
        description_id INTEGER NOT NULL,
        city_id        INTEGER NOT NULL,
        company_id     INTEGER NOT NULL,
        FOREIGN KEY (description_id) REFERENCES DESCRIPTION(description_id),
        FOREIGN KEY (city_id)        REFERENCES CITY(city_id),
        FOREIGN KEY (company_id)     REFERENCES COMPANY(company_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DEGREE (
        degree_id INTEGER PRIMARY KEY,
        degree    TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS SKILL (
        skill_id INTEGER PRIMARY KEY,
        skill    TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS OFFER_DEGREE (
        offer_id  INTEGER NOT NULL,
        degree_id INTEGER NOT NULL,
        PRIMARY KEY (offer_id, degree_id),
        FOREIGN KEY (offer_id)  REFERENCES OFFER(offer_id)  ON DELETE CASCADE,
        FOREIGN KEY (degree_id) REFERENCES DEGREE(degree_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS OFFER_SKILL (
        offer_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        PRIMARY KEY (offer_id, skill_id),
        FOREIGN KEY (offer_id) REFERENCES OFFER(offer_id)  ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id)
    );
    """
]

for stmt in schema_statements:
    cursor.execute(stmt)

connection.commit()
connection.close()