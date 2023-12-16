import click


@click.command()
@click.pass_context
def fragrantica(ctx):
    click.echo("This is the Fragrantica package.")
