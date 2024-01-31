import click

from fragscrape.fragrantica.load import load
from fragscrape.fragrantica.process import process
from fragscrape.fragrantica.visualize import visualize


@click.group()
@click.pass_context
def fragrantica(ctx):
    """Entrypoint for Fragrantica-specific code."""


fragrantica.add_command(load)
fragrantica.add_command(process)
fragrantica.add_command(visualize)
