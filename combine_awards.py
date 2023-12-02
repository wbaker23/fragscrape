import pandas as pd

if __name__ == "__main__":
    # Load all 6 .csv files and show the number of total rows
    df_17 = pd.read_csv("mens_all_time_2017.csv", index_col="link").add_suffix("_17")
    df_17["inverse_rank_17"] = df_17.shape[0] - df_17["order_17"] + 1
    df_18 = pd.read_csv("mens_all_time_2018.csv", index_col="link").add_suffix("_18")
    df_18["inverse_rank_18"] = df_18.shape[0] - df_18["order_18"] + 1
    df_19 = pd.read_csv("mens_all_time_2019.csv", index_col="link").add_suffix("_19")
    df_19["inverse_rank_19"] = df_19.shape[0] - df_19["order_19"] + 1
    df_20 = pd.read_csv("mens_all_time_2020.csv", index_col="link").add_suffix("_20")
    df_20["inverse_rank_20"] = df_20.shape[0] - df_20["order_20"] + 1
    df_21 = pd.read_csv("mens_all_time_2021.csv", index_col="link").add_suffix("_21")
    df_21["inverse_rank_21"] = df_21.shape[0] - df_21["order_21"] + 1
    df_22 = pd.read_csv("mens_all_time_2022.csv", index_col="link").add_suffix("_22")
    df_22["inverse_rank_22"] = df_22.shape[0] - df_22["order_22"] + 1

    print(
        f"{df_17.shape[0] + df_18.shape[0] + df_19.shape[0] + df_20.shape[0] + df_21.shape[0] + df_22.shape[0]} total rows"
    )

    # Combine all 6 dataframes and calculate totals columns
    df_combined = pd.concat([df_17, df_18, df_19, df_20, df_21, df_22], axis=1)
    df_combined["upvotes_total"] = df_combined[
        [
            "upvotes_17",
            "upvotes_18",
            "upvotes_19",
            "upvotes_20",
            "upvotes_21",
            "upvotes_22",
        ]
    ].sum(axis=1)
    df_combined["downvotes_total"] = df_combined[
        [
            "downvotes_17",
            "downvotes_18",
            "downvotes_19",
            "downvotes_20",
            "downvotes_21",
            "downvotes_22",
        ]
    ].sum(axis=1)
    df_combined["inverse_rank_total"] = df_combined[
        [
            "inverse_rank_17",
            "inverse_rank_18",
            "inverse_rank_19",
            "inverse_rank_20",
            "inverse_rank_21",
            "inverse_rank_22",
        ]
    ].sum(axis=1)

    # Remove rows from the combined dataframe which do not have the same fragrance name across years
    df_combined["check_names"] = (
        df_combined[
            ["name_17", "name_18", "name_19", "name_20", "name_21", "name_22"]
        ].nunique(axis=1)
        == 1
    )
    print(
        f"{df_combined[~df_combined['check_names']].shape[0]} record has a name that does not match across years"
    )
    df_combined = df_combined[df_combined["check_names"]]

    # Coalesce name columns
    df_combined["name"] = (
        df_combined["name_17"]
        .combine_first(df_combined["name_18"])
        .combine_first(df_combined["name_19"])
        .combine_first(df_combined["name_20"])
        .combine_first(df_combined["name_21"])
        .combine_first(df_combined["name_22"])
    )

    # Drop unused columns and print final number of rows
    df_combined.drop(
        columns=[
            "check_names",
            "name_17",
            "name_18",
            "name_19",
            "name_20",
            "name_21",
            "name_22",
        ],
        inplace=True,
    )
    print(f"{df_combined.shape[0]} rows")

    # Write combined dataframe to Excel file
    df_combined.to_csv("mens_all_time_combined.csv")
