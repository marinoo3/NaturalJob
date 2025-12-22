import sqlean as sqlite3
import sqlite_vec

connection = sqlite3.connect("data/db/offer.db")
connection.enable_load_extension(True)
sqlite_vec.load(connection)
connection.execute("PRAGMA foreign_keys = ON;")
cursor = connection.cursor()

schema_statements = [
    """
    CREATE TABLE IF NOT EXISTS COMPANY (
        company_id   INTEGER PRIMARY KEY,
        name         TEXT,
        description  TEXT,
        industry     TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS REGION (
        region_id INTEGER PRIMARY KEY,
        code      TEXT,
        name      TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS CITY (
        city_id   INTEGER PRIMARY KEY,
        name      TEXT,
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
    # TODO: Maybe I shouldn't set cluster_id to primary key
    """
    CREATE TABLE IF NOT EXISTS CLUSTER (
        cluster_id    INTEGER PRIMARY KEY,
        cluster_name  TEXT,
        main_tokens   TEXT NOT NULL
    );
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS TFIDF
    USING vec0(
        emb_50d  FLOAT[50],
        emb_3d   FLOAT[3]
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS OFFER (
        offer_id       INTEGER PRIMARY KEY,
        title          TEXT NOT NULL,
        job_name       TEXT,
        job_type       TEXT,
        contract_type  TEXT,
        salary_label   TEXT,
        salary_min     REAL,
        salary_max     REAL,
        min_experience TEXT,
        latitude       REAL,
        longitude      REAL,
        date           TEXT,
        source         TEXT NOT NULL,
        description_id INTEGER NOT NULL,
        city_id        INTEGER NOT NULL,
        company_id     INTEGER NOT NULL,
        cluster_id     INTEGER,
        tfidf_id       INTEGER,
        FOREIGN KEY (description_id) REFERENCES DESCRIPTION(description_id),
        FOREIGN KEY (city_id)        REFERENCES CITY(city_id),
        FOREIGN KEY (company_id)     REFERENCES COMPANY(company_id),
        FOREIGN KEY (cluster_id)     REFERENCES CLUSTER(cluster_id),
        FOREIGN KEY (tfidf_id)       REFERENCES TFIDF(rowid)
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