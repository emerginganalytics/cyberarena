import click
from common.publish_compute_image import create_production_image
from common.globals import ds_client, BUILD_STATES
from common.delete_expired_workouts import delete_specific_workout
from common.state_transition import state_transition


@click.command()
@click.argument('server_name')
def create_image(server_name):
    """
    Creates a new image based on an existing server in the project.
    :param server_name: The name of the server to image.
    """
    if create_production_image(server_name):
        print(f"Successfully started the image creation of {server_name}")


if __name__ == "__main__":
    create_image()
