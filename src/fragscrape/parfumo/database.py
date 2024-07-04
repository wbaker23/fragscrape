import sqlite3


def db_cursor(func):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect("fragscrape.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        result = func(cur, *args, **kwargs)

        con.commit()
        con.close()

        return result

    return wrapper


def db_connection(func):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect("fragscrape.db")
        con.row_factory = sqlite3.Row

        result = func(con, *args, **kwargs)

        con.commit()
        con.close()

        return result

    return wrapper


@db_cursor
def initialize(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS collection (
            name, 
            brand, 
            link PRIMARY KEY, 
            image_src, 
            collection_group, 
            wearings
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tops (
            name, 
            brand, 
            link PRIMARY KEY, 
            image_src, 
            tops_group
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS votes (
            link, 
            category, 
            votes, 
            PRIMARY KEY (link, category)
        )
        """
    )
