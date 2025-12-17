import sqlite3
from datetime import date
import os

from .models import Offer, Description, City, Region, Company




class OfferDB():

    path = 'db/offer.db'

    def __init__(self) -> None:
        root = os.environ.get('DATA_PATH', 'data/')
        self.db_path = os.path.join(root, self.path)

    def _get_or_create_region(self, cur:sqlite3.Cursor, region:Region) -> int:
        row = cur.execute(
            "SELECT region_id FROM REGION WHERE code = ?", [region.code]
        ).fetchone()
        if row:
            return row[0]

        cur.execute(
            "INSERT INTO REGION(code, name) VALUES (?, ?)", [region.code, region.name]
        )
        return cur.lastrowid
    
    def _get_or_create_city(self, cur:sqlite3.Cursor, city:City, region_id:int) -> int:
        row = cur.execute(
            "SELECT city_id FROM CITY WHERE name = ? AND region_id = ?", [city.name, region_id]
        ).fetchone()
        if row:
            return row[0]

        cur.execute(
            "INSERT INTO CITY(name, region_id) VALUES (?, ?)", [city.name, region_id]
        )
        return cur.lastrowid
    
    def _get_or_create_company(self, cur:sqlite3.Cursor, company:Company) -> int:
        row = cur.execute(
            "SELECT company_id FROM COMPANY WHERE name = ?", [company.name]
        ).fetchone()
        if row:
            return row[0]
        
        cur.execute(
            "INSERT INTO COMPANY(name, description, industry) VALUES (?, ?, ?)",
            [company.name, company.description, company.industry]
        )
        return cur.lastrowid
    
    def _insert_description(self, cur:sqlite3.Cursor, description:Description) -> int:
        cur.execute(
            "INSERT INTO DESCRIPTION(offer_description, profile_description) VALUES (?, ?)",
            [description.offer_description, description.profile_description]
        )
        return cur.lastrowid
    
    def _insert_offer(self, cur:sqlite3.Cursor, offer:Offer, company_id:int, city_id:int, description_id:int) -> int:
        # Try to fetch the existing ID (skip duplicates)
        existing = cur.execute(
            """
            SELECT offer_id
            FROM OFFER
            WHERE title = ? AND company_id = ? AND date = ?
            """,
            [offer.title, company_id, offer.date]
        ).fetchone()
        if existing:
            return existing[0]

        cur.execute(
            """
            INSERT INTO OFFER
                (title, job_name, job_type, contract_type,
                 salary_label, salary_min, salary_max, min_experience, latitude, longitude,
                 date, source,
                 description_id, city_id, company_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                offer.title,
                offer.job_name,
                offer.job_type,
                offer.contract_type,
                offer.salary_label,
                offer.salary_min,
                offer.salary_max,
                offer.min_experience,
                offer.latitude,
                offer.longitude,
                offer.date,
                offer.source,
                description_id,
                city_id,
                company_id
            ]
        )
        return cur.lastrowid
    
    def _sync_degrees(self, cur:sqlite3.Cursor, offer_id:int, degrees:list[str]) -> None:
        for degree in degrees:
            degree_id = self._get_or_create_degree(cur, degree)
            cur.execute(
                "INSERT OR IGNORE INTO OFFER_DEGREE(offer_id, degree_id) VALUES (?, ?)",
                [offer_id, degree_id]
            )

    def _sync_skills(self, cur:sqlite3.Cursor, offer_id:int, skills:list[str]) -> None:
        for skill in skills:
            skill_id = self._get_or_create_skill(cur, skill)
            cur.execute(
                "INSERT OR IGNORE INTO OFFER_SKILL(offer_id, skill_id) VALUES (?, ?)",
                [offer_id, skill_id]
            )

    def _get_or_create_degree(self, cur:sqlite3.Cursor, degree:str) -> int:
        row = cur.execute(
            "SELECT degree_id FROM DEGREE WHERE degree = ?", [degree]
        ).fetchone()
        if row:
            return row[0]

        cur.execute("INSERT INTO DEGREE(degree) VALUES (?)", [degree])
        return cur.lastrowid
    
    def _get_or_create_skill(self, cur:sqlite3.Cursor, skill:str) -> int:
        row = cur.execute(
            "SELECT skill_id FROM SKILL WHERE skill = ?", [skill]
        ).fetchone()
        if row:
            return row[0]

        cur.execute("INSERT INTO SKILL(skill) VALUES (?)", [skill])
        return cur.lastrowid

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def add(self, offers:list[Offer]) -> int:
        """Insert offers into database.
        
        Args:
            offers (list[Offer]): List of offers to add to db
        """

        with self.connect() as conn:
            cur = conn.cursor()

            for offer in offers:
                region_id = self._get_or_create_region(cur, offer.city.region)
                city_id = self._get_or_create_city(cur, offer.city, region_id)
                company_id = self._get_or_create_company(cur, offer.company)
                description_id = self._insert_description(cur, offer.description)

                offer_id = self._insert_offer(
                    cur,
                    offer,
                    company_id=company_id,
                    city_id=city_id,
                    description_id=description_id,
                )

                self._sync_degrees(cur, offer_id, offer.degrees)
                self._sync_skills(cur, offer_id, offer.skills)

            conn.commit()
    
    def get_latest_date(self, source:str=None) -> date|None:
        """Search the latest date from database

        Args:
            source (str, optional): The source from which to search the last offer's date, strict latest if None.

        Returns:
            datetime: The latest date
        """

        with self.connect() as conn:
            cur = conn.cursor()
            if source:
                cur.execute(
                    "SELECT date FROM OFFER WHERE source = ? ORDER BY date DESC LIMIT 1", [source]
                )
            else:
                cur.execute(
                    "SELECT date FROM OFFER ORDER BY date DESC LIMIT 1"
                )

            row = cur.fetchone()
            if not row:
                return None
            
        return date.fromisoformat(row[0])