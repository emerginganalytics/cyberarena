from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from common.publish_compute_image import create_production_image

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--server", default=None, help="The server to image")

args = vars(parser.parse_args())

# Set up parameters
server_name = args['server']


def create_image(server_name):
    """
    Creates a new image based on an existing server in the project.
    :param server_name: The name of the server to image.
    """
    if create_production_image(server_name):
        print(f"Successfully started the image creation of {server_name}")


if __name__ == "__main__":
    create_image(server_name)
