import click

from fragscrape.parfumo.compare_types import compare_types
from fragscrape.parfumo.create_graph import create_graph
from fragscrape.parfumo.display_graph import display_graph
from fragscrape.parfumo.enrich_fragrances import enrich_fragrances
from fragscrape.parfumo.import_fragrances import import_fragrances


@click.group()
@click.pass_context
def parfumo(ctx):
    """Entrypoint for Parfumo-specific code."""
    pass


parfumo.add_command(import_fragrances)
parfumo.add_command(enrich_fragrances)
parfumo.add_command(create_graph)
parfumo.add_command(display_graph)
parfumo.add_command(compare_types)
