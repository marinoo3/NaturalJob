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
    
    def _row_to_offer(self, row: sqlite3.Row) -> Offer:
        degrees = row["degrees"].split("||") if row["degrees"] else []
        skills = row["skills"].split("||") if row["skills"] else []

        return Offer(
            title=row["title"],
            job_name=row["job_name"],
            job_type=row["job_type"],
            contract_type=row["contract_type"],
            salary_label=row["salary_label"],
            salary_min=row["salary_min"],
            salary_max=row["salary_max"],
            min_experience=row["min_experience"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            date=row["date"],
            source=row["source"],
            description=Description(
                offer_description=row["offer_description"],
                profile_description=row["profile_description"],
            ),
            company=Company(
                name=row["company_name"],
                description=row["company_description"],
                industry=row["company_industry"],
            ),
            city=City(
                name=row["city_name"],
                region=Region(
                    code=row["region_code"],
                    name=row["region_name"],
                ),
            ),
            degrees=degrees,
            skills=skills,
        )

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

    def get(self, id:str=None) -> list[Offer]:
        """Get an offer by id, returns all offers if no ID.

        Args:
            id (str, optional): Offer ID. Defaults to None.

        Returns:
            Offer|list[Offer]: Offers
        """

        with self.connect() as conn:
            cur = conn.cursor()

            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = """
            SELECT
                o.offer_id,
                o.title,
                o.job_name,
                o.job_type,
                o.contract_type,
                o.salary_label,
                o.salary_min,
                o.salary_max,
                o.min_experience,
                o.latitude,
                o.longitude,
                o.date,
                o.source,
                c.name AS company_name,
                c.description AS company_description,
                c.industry AS company_industry,
                ci.name AS city_name,
                r.code AS region_code,
                r.name AS region_name,
                d.offer_description,
                d.profile_description,
                (SELECT GROUP_CONCAT(de.degree, '||')
                   FROM OFFER_DEGREE od
                   JOIN degree de ON de.degree_id = od.degree_id
                  WHERE od.offer_id = o.offer_id) AS degrees,
                (SELECT GROUP_CONCAT(s.skill, '||')
                   FROM OFFER_SKILL os
                   JOIN skill s ON s.skill_id = os.skill_id
                  WHERE os.offer_id = o.offer_id) AS skills
            FROM OFFER o
            JOIN COMPANY c     ON c.company_id     = o.company_id
            JOIN DESCRIPTION d ON d.description_id = o.description_id
            JOIN CITY ci        ON ci.city_id       = o.city_id
            JOIN REGION r       ON r.region_id      = ci.region_id
            WHERE (?1 IS NULL OR o.offer_id = ?1)
            ORDER BY o.date DESC;
            """

            cur.execute(sql, (id,))
            rows = cur.fetchall()

            if id is not None:
                return self._row_to_offer(rows[0]) if rows else None
            return [self._row_to_offer(row) for row in rows]



    def summary(self, source:str=None) -> list[dict]:
        with self.connect() as conn:
            cur = conn.cursor()
            # Get column metadata (name, declared type, etc.)
            cur.execute("PRAGMA table_info('OFFER')")
            columns = cur.fetchall()

            summary = []
            for cid, name, type, notnull, _, pk in columns:
                # Count NULLs in this column
                if source:
                    cur.execute(
                        f"SELECT COUNT(*) FROM OFFER WHERE source = ? and {name} IS NULL", [source]
                    )
                else:
                    cur.execute(
                        "SELECT COUNT(*) FROM OFFER WHERE ? IS NULL", [name]
                    )
                na_count = cur.fetchone()[0]
                summary.append({
                    'name': name,
                    'id': cid,
                    'na': na_count,
                    'not_null': bool(notnull),
                    'type': type,
                    'pk': bool(pk)
                })

            return summary

    def get_total(self, source:str|None) -> int:
        """Get count from a specific source, or all source if `source` is None.

        Args:
            source (str | None): The source ('NTNE', 'APEC', None)

        Returns:
            int: Total count of offers
        """

        with self.connect() as conn:
            cur = conn.cursor()
            if source:
                cur.execute(
                    "SELECT count(offer_id) FROM OFFER WHERE source = ?", [source]
                )
            else:
                cur.execute(
                    "SELECT count(offer_id) FROM OFFER"
                )
            count = cur.fetchone()[0]
        return count
            
    
    def get_latest_date(self, source:str=None, isostring=False) -> date|None:
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
        
        latest = date.fromisoformat(row[0])
        if isostring:
            latest = latest.isoformat() 
        return latest