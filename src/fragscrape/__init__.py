import click

from fragscrape.fragrantica import fragrantica
from fragscrape.parfumo import parfumo


@click.group()
@click.pass_context
def cli(ctx):
    """Prints a greeting."""
    click.echo("Hello, World!")


cli.add_command(fragrantica)
cli.add_command(parfumo)
