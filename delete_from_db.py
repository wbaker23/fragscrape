from fragscrape.parfumo.database import db_cursor


@db_cursor
def delete_with_link(cursor, link):
    cursor.execute(f"DELETE FROM collection WHERE link = '{link}'")


if __name__ == "__main__":
    link = "https://www.parfumo.com/Perfumes/Hugo_Boss/boss-bottled-absolu"
    delete_with_link(link=link)
