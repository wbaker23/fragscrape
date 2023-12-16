import click


@click.command()
@click.pass_context
def parfumo(ctx):
    click.echo("This is the Parfumo package.")
