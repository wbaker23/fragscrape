import pandas as pd

if __name__ == "__main__":
    # Load all 6 .csv files and show the number of total rows
    df_17 = pd.read_csv(
        "data/processed/mens_all_time_2017.csv", index_col="link"
    ).add_suffix("_17")
    df_18 = pd.read_csv(
        "data/processed/mens_all_time_2018.csv", index_col="link"
    ).add_suffix("_18")
    df_19 = pd.read_csv(
        "data/processed/mens_all_time_2019.csv", index_col="link"
    ).add_suffix("_19")
    df_20 = pd.read_csv(
        "data/processed/mens_all_time_2020.csv", index_col="link"
    ).add_suffix("_20")
    df_21 = pd.read_csv(
        "data/processed/mens_all_time_2021.csv", index_col="link"
    ).add_suffix("_21")
    df_22 = pd.read_csv(
        "data/processed/mens_all_time_2022.csv", index_col="link"
    ).add_suffix("_22")
    df_23 = pd.read_csv(
        "data/processed/mens_all_time_2023.csv", index_col="link"
    ).add_suffix("_23")

    # Combine all 6 dataframes and calculate mean columns
    df_combined = pd.concat([df_17, df_18, df_19, df_20, df_21, df_22, df_23], axis=1)
    df_combined["vote_diff"] = df_combined[
        [
            "vote_diff_17",
            "vote_diff_18",
            "vote_diff_19",
            "vote_diff_20",
            "vote_diff_21",
            "vote_diff_22",
            "vote_diff_23",
        ]
    ].mean(axis=1)
    df_combined["updated_order"] = df_combined[
        [
            "updated_order_17",
            "updated_order_18",
            "updated_order_19",
            "updated_order_20",
            "updated_order_21",
            "updated_order_22",
            "updated_order_23",
        ]
    ].mean(axis=1)
    df_combined["bayes"] = df_combined[
        [
            "bayes_17",
            "bayes_18",
            "bayes_19",
            "bayes_20",
            "bayes_21",
            "bayes_22",
            "bayes_23",
        ]
    ].mean(axis=1)
    df_combined["vote_diff_normalized"] = df_combined[
        [
            "vote_diff_normalized_17",
            "vote_diff_normalized_18",
            "vote_diff_normalized_19",
            "vote_diff_normalized_20",
            "vote_diff_normalized_21",
            "vote_diff_normalized_22",
            "vote_diff_normalized_23",
        ]
    ].mean(axis=1)
    df_combined["total_votes"] = df_combined[
        [
            "total_votes_17",
            "total_votes_18",
            "total_votes_19",
            "total_votes_20",
            "total_votes_21",
            "total_votes_22",
            "total_votes_23",
        ]
    ].mean(axis=1)

    # Remove rows from the combined dataframe which do not have the same fragrance name across years
    df_combined["check_names"] = (
        df_combined[
            [
                "name_17",
                "name_18",
                "name_19",
                "name_20",
                "name_21",
                "name_22",
                "name_23",
            ]
        ].nunique(axis=1)
        == 1
    )
    print(
        f"{df_combined[~df_combined['check_names']].shape[0]} record has a name that does not match across years."
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
        .combine_first(df_combined["name_23"])
    )

    # Drop unused columns and print final number of rows
    df_combined.drop(
        columns=[
            col
            for col in df_combined.columns.to_list()
            if col[-3:] in ["_17", "_18", "_19", "_20", "_21", "_22", "_23"]
        ]
        + ["check_names"],
        inplace=True,
    )
    print(f"{df_combined.shape[0]} rows in combined DataFrame.")

    # Write combined dataframe to Excel file
    df_combined.sort_values("total_votes", ascending=False).head(200).to_csv(
        "data/processed/mens_all_time_combined.csv"
    )
