import click

from fragscrape.parfumo.compare import compare
from fragscrape.parfumo.create_graph import create_graph
from fragscrape.parfumo.display_graph import display_graph
from fragscrape.parfumo.enrich import enrich
from fragscrape.parfumo.load import load


@click.group()
@click.pass_context
def parfumo(ctx):
    """Entrypoint for Parfumo-specific code."""
    pass


parfumo.add_command(load)
parfumo.add_command(enrich)
parfumo.add_command(create_graph)
parfumo.add_command(display_graph)
parfumo.add_command(compare)
