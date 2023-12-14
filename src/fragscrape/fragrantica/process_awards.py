import argparse
import re

import numpy as np
import pandas as pd
from fragscrape.fragrantica.config import *
from sklearn.preprocessing import MinMaxScaler

parser = argparse.ArgumentParser(
    description="Enrich the data from a Fragrantica awards page."
)
parser.add_argument("filename", help="The path of the file to process.")
parser.add_argument("output", help="The path of the file to write.")
args = parser.parse_args()

if __name__ == "__main__":
    # Load data
    df = pd.read_csv(args.filename)
    print(f"{df.shape[0]} fragrances loaded from {args.filename}")

    # Filter out fragrances with either zero upvotes or zero downvotes
    df = df[(df["upvotes"] != 0) & (df["downvotes"] != 0)]

    # Get rid of bottom 10% of fragrances.
    # These are skewed negative due to reinforcement of negative votes
    # by being visible at the bottom of the list.
    df = df[df["order"] <= df["order"].quantile(0.9)]

    # Add feature columns
    df["total_votes"] = df["upvotes"] + df["downvotes"]
    df["vote_diff"] = df["upvotes"] - df["downvotes"]
    df["vote_diff_normalized"] = MinMaxScaler().fit_transform(
        np.array(df["vote_diff"]).reshape(-1, 1)
    )
    df["ratio"] = df["upvotes"] / df["total_votes"]
    df["updated_order"] = df["order"].rank()
    df["inverse_order"] = df.shape[0] - df["order"].rank() + 1
    df["bayes"] = (df["upvotes"] + df["upvotes"].median()) / (
        df["upvotes"]
        + df["upvotes"].median()
        + df["downvotes"]
        + df["downvotes"].median()
    )

    # Write output
    df.to_csv(args.output, index=False)
