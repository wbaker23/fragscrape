import click
import matplotlib.pyplot as plt
import mplcursors
import pandas as pd


@click.command()
@click.pass_context
@click.option("-f", "--filename", "filename")
def visualize(ctx, filename):
    # Load data
    df_combined = pd.read_csv(filename)
    print(f"{df_combined.shape[0]} fragrances loaded from {filename}")

    # Make scatter plot
    plt.close("all")
    fig, ax = plt.subplots(2)
    fig.tight_layout(h_pad=4)
    ax[0].set_title("Scatter Plot of Vote Diff vs Rank")
    ax[0].set(xlabel="Rank")
    ax[0].set(ylabel="Vote Difference")

    # Plot x and y
    y = df_combined["vote_diff"]
    # y = y.apply(np.log)
    x = df_combined["updated_order"]
    # x = x.apply(np.log)
    sc1 = ax[0].scatter(x, y, s=10)

    y2 = df_combined["bayes"]
    sc2 = ax[1].scatter(x, y2, s=10)
    ax[1].set_title("Scatter Plot of Bayesian Avg vs Rank")
    ax[1].set(xlabel="Rank")
    ax[1].set(ylabel="Bayesian Avg Ratio")

    # Plot best-fit curve
    # fit_function = exponential
    # params, covariance = curve_fit(fit_function, x, y, p0=[1, 10, 700, 1])
    # print(params)
    # xhat = np.linspace(x.min(), x.max(), 100)
    # ax[0].plot(xhat, fit_function(xhat, *params), color="k")

    # Calculate & plot residuals
    # df_combined["yhat"] = fit_function(x, *params)
    # df_combined["residual"] = y - df_combined["yhat"]
    # sc2 = ax[1].scatter(x, df_combined["residual"], s=10)
    # ax[1].axhline(color="k")
    # ax[1].set_title("Residual Plot")
    # ax[1].set(xlabel="Inverse of Order")
    # ax[1].set(ylabel="Residual")

    # Add cursors
    cursor1 = mplcursors.cursor(sc1, hover=False)
    cursor2 = mplcursors.cursor(sc2, hover=False)

    @cursor1.connect("add")
    @cursor2.connect("add")
    def on_add(sel):
        sel.annotation.set(
            text=df_combined[
                [
                    "name",
                    "vote_diff_normalized",
                    "total_votes",
                    "updated_order",
                    "bayes",
                ]
            ]
            .iloc[sel.index]
            .to_string()
        )

    # Box plot of residuals to see outliers
    # residual_boxplot = df_combined.boxplot("residual", ax=ax[2], vert=False)

    # Show figure
    plt.show()

    df_combined[~df_combined["name"].str.contains("\(female\)")].sort_values(
        "bayes", ascending=False
    ).head(50)

    # residual_q1 = df_combined["residual"].quantile(0.25)
    # residual_q3 = df_combined["residual"].quantile(0.75)
    # residual_iqr = residual_q3 - residual_q1

    # df_combined[
    #     (df_combined["residual"] > (residual_q3 + 1.5 * residual_iqr))
    #     | (df_combined["residual"] < (residual_q1 - 1.5 * residual_iqr))
    # ].sort_values("residual")
