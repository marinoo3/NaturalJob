import sqlite3



class OfferTable():

    def add(self, offers:list[dict]) -> None:
        """Add offers to OFFER table. Duplicated element are skipped

        Args:
            offers (list[dict]): Offers to add
        """

        