import click
import yaml

from fragscrape.fragrantica import fragrantica
from fragscrape.parfumo import parfumo


@click.group()
@click.pass_context
@click.option("--config-file", "-f", "config_file", default="config.yaml")
def cli(ctx, config_file):
    """Entrypoint for fragscrape package."""
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    ctx.ensure_object(dict)
    ctx.obj["config"] = config


cli.add_command(fragrantica)
cli.add_command(parfumo)
