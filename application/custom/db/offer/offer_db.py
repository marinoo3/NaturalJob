import sqlite3
import sqlite_vec
from datetime import date
import os
import numpy as np

from .models import Offer, Description, City, Region, Company, Cluster




class OfferDB:

    path = 'db/offer.db'

    def __init__(self) -> None:
        root = os.environ.get('DATA_PATH', 'data/')
        self.db_path = os.path.join(root, self.path)

    @staticmethod
    def _vecf32_converter(blob:bytes) -> np.ndarray:
        # copy() so the array owns the memory even after SQLite frees the buffer
        return np.frombuffer(blob, dtype=np.float32).copy()

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

    def _get_or_create_cluster(self, cur:sqlite3.Cursor, cluster:Cluster) -> int:
        row = cur.execute(
            "SELECT cluster_id FROM CLUSTER WHERE cluster_id = ?", [cluster.id]
        ).fetchone()
        if row:
            return row[0]

        cur.execute("INSERT INTO CLUSTER(cluster_id, cluster_name, main_tokens) VALUES (?, ?, ?)", [cluster.id, cluster.name, cluster.main_tokens])
        return cluster.id

    def _row_to_offer(self, row:sqlite3.Row) -> Offer:
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
    
    def _row_to_cluster(self, row:sqlite3.Row) -> Cluster:
        return Cluster(
            id=row['cluster_id'],
            name=row['cluster_name'],
            main_tokens=row['main_tokens']
        )

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn) 
        return conn
    
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

    def add_nlp(self, conn:sqlite3.Connection, offer_id:int, emb_50d:np.ndarray=None, emb_3d:np.ndarray=None, cluster:Cluster=None) -> None:
        """Add offer's nlp data to db. Skip non provided data.

        Args:
            conn (sqlite3.Connection): Database connection
            offer_id (int): The ID of the offer
            emb_50d (np.ndarray, optional): 50 dimenssions embeddings. Default to None
            emb_3d (np.ndarray, optional): 3 dimenssions embeddings. Default to None
            cluster (Cluster, optional): The offer cluster object. Default to None
        """

        cur = conn.cursor()
        
        if cluster:
            cluster_id = self._get_or_create_cluster(cur, cluster)
            cur.execute(
                "UPDATE OFFER SET cluster_id = ? WHERE offer_id = ?", 
                [cluster_id, offer_id]
            )

        if emb_50d is not None and emb_3d is not None:
            cur.execute(
                "INSERT INTO TFIDF(emb_50d, emb_3d) VALUES (vec_f32(?), vec_f32(?))", 
                [emb_50d.tobytes(), emb_3d.tobytes()]
            )
            tfidf_id = cur.lastrowid
            cur.execute(
                "UPDATE OFFER SET tfidf_id = ? WHERE offer_id = ?", 
                [tfidf_id, offer_id]
            )

    def update_clusters(self, conn:sqlite3.Connection, cluster:Cluster):
        """Update offer's nlp data on db. Update only provided data, skip Nones.

        Args:
            conn (sqlite3.Connection): _description_
            cluster (Cluster): The offer cluster object. Default to None
        """

        curr = conn.cursor()

    def search_offer(self, id:str=None) -> tuple[list[Offer], list[int]]:
        """Search an offer by id, returns all offers if no ID.

        Args:
            id (str, optional): Offer ID. Defaults to None.

        Returns:
            list[Offer]: Offers
            list[int]: Offer IDs
        """

        with self.connect() as conn:
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

            return [self._row_to_offer(row) for row in rows], [row['offer_id'] for row in rows]
        
    def search_clusters(self, id:str=None) -> list[Cluster]:
        """Search an offer cluster by id, returns all offer clusters if no ID.

        Args:
            id (str, optional): Offer ID. Defaults to None.

        Returns:
            list[Cluster]: Offer clusters
        """

        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = """
            SELECT 
                c.ROWID as cluster_id, c.cluster_name, c.main_tokens, o.title
            FROM OFFER o
            JOIN CLUSTER c ON c.ROWID = o.cluster_id
            WHERE (?1 IS NULL OR o.offer_id = ?1)
            """

            cur.execute(sql, (id,))
            rows = cur.fetchall()

            return [self._row_to_cluster(row) for row in rows], [row['title'] for row in rows]

    def get_table(self, table_name:str, columns:list[str]=None, convert_blob=False) -> list:
        """Get the content of a table from OFFER db

        Args:
            table_name (str): The name of the table
            columns (list[str], optional): The list of columns to select, all if not provided. Default to None
            convert_blob (bool): To convert the result to vectors (if stored as blob from sqlite-vec). Default to None

        Returns:
            list: Result
        """

        with self.connect() as conn:
            cur = conn.cursor()
            if columns:
                cols = ', '.join(columns)
                cur.execute(f"SELECT {cols} FROM {table_name}")
            else:
                cur.execute(f"SELECT * FROM {table_name}")

            content = cur.fetchall()

            result = []
            for row in content:
                if convert_blob:
                    # Decode blob to np array
                    row = [self._vecf32_converter(blob) for blob in row]
                if columns and len(columns) == 1:
                    # Convert 3d array to 2d if only 1 item
                    row = row[0]
                result.append(row)

            return result

    def clear_table(self, conn:sqlite3.Connection, table_name:str) -> None:
        """Delete the content of a database table. Warning this action is permanent.

        Args:
            table_name (str): The name of the table to clear
        """

        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table_name}")

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
    
    def get_unprocessed(self, source=None) -> tuple[list[int], list[str]]:

        with self.connect() as conn:
            cur = conn.cursor()
            if source:
                cur.execute(
                    """
                    SELECT o.offer_id, d.offer_description
                    FROM OFFER AS o
                    JOIN DESCRIPTION AS d ON d.description_id = o.description_id
                    WHERE o.source = ? and o.cluster_id IS NULL
                    """, [source]
                )
            else:
                cur.execute(
                    """
                    SELECT o.offer_id, d.offer_description
                    FROM OFFER AS o
                    JOIN DESCRIPTION AS d ON d.description_id = o.description_id
                    WHERE o.cluster_id IS NULL
                    """
                )

            result = cur.fetchall()
            ids = [row[0] for row in result]
            descriptions = [row[1] for row in result]
            return ids, descriptions

