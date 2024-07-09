from fragscrape.parfumo.database import query_to_df

if __name__ == "__main__":
    print(
        query_to_df(
            "SELECT * FROM collection WHERE link NOT IN (SELECT link FROM votes)"
        )
    )
    print(query_to_df("SELECT * FROM tops WHERE link NOT IN (SELECT link FROM votes)"))
