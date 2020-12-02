import googleapiclient.discovery
from googleapiclient.errors import HttpError
from socket import timeout

from common.globals import project, zone, gcp_operation_wait


def create_snapshot_from_disk(disk):
    """
    This function keeps at most 2 snapshot available from a server
    param disk: The name of the server
    return: Either the name of the new snapshot or None
    """
    service = googleapiclient.discovery.build('compute', 'v1')

    found_available = False
    latest = 0
    latest_ts = '2000-01-01T00:00:00.000'
    i = 0
    while i < 3:
        try:
            response = service.snapshots().get(project=project, snapshot=disk + str(i)).execute()
            if response['creationTimestamp'] > latest_ts:
                latest_ts = response['creationTimestamp']
                latest = i
            i += 1
        except HttpError:
            latest = (i - 1) % 3
            found_available = True
            break

    selected_disk = f"{disk}{(latest + 1) % 3}"
    if not found_available:
        response = service.snapshots().delete(project=project, snapshot=selected_disk).execute()

        if not gcp_operation_wait(service=service, response=response, wait_type="global"):
            raise Exception(f"Timeout waiting for snapshot {selected_disk} to delete.")

    snapshot_body = {
        'name': selected_disk,
        'description': 'Production snapshot used for imaging'
    }

    response = service.disks().createSnapshot(project=project, zone=zone, disk=disk, body=snapshot_body).execute()

    if not gcp_operation_wait(service=service, response=response):
        raise Exception(f"Timeout waiting for snapshot {selected_disk} to be created")

    return selected_disk


def create_production_image(server_name, existing_snapshot=None):
    """
    Create a new production image.
    :param image_version: The version of the image as determined by the application
    :param server_name: Used for testing to provide an existing snapshot to image
    :param existing_snapshot: Provided for testing purposes if a snapshot already exists
    :returns: None
    """
    # First try and create a new snapshot image.
    if existing_snapshot:
        snapshot_name = existing_snapshot
    else:
        snapshot_name = create_snapshot_from_disk(server_name)

    if snapshot_name:
        prod_image = f'image-{server_name}'
        service = googleapiclient.discovery.build('compute', 'v1')
        i = 0
        delete_success = False
        nothing_to_delete = False
        while not delete_success and i < 5 and not nothing_to_delete:
            try:
                response = service.images().delete(project=project, image=prod_image).execute()
                delete_success = True
                print(f'Sent job to delete the production image before creating a new one, and waiting for response')
            except HttpError:
                nothing_to_delete = True
            except BrokenPipeError:
                i += 1
        if not delete_success and not nothing_to_delete:
            raise Exception(f"Error deleting image {prod_image}")

        if not nothing_to_delete:
            if not gcp_operation_wait(service=service, response=response, wait_type="global"):
                raise Exception(f"Timeout waiting for image {prod_image} to delete.")


        # If the image was successfully deleted, then build the new image.
        image_body = {
            'name': prod_image,
            'description': 'Cyber Gym production image',
            'sourceSnapshot': f'projects/{project}/global/snapshots/{snapshot_name}'
        }
        i = 0
        build_success = False
        while not build_success and i < 5:
            try:
                response = service.images().insert(project=project, body=image_body).execute()
                build_success = True
                print(f'Sent job to create the new production image, and waiting for response')
            except BrokenPipeError:
                i += 1
        return True
    else:
        print(f"Error in publishing production image. Timeout waiting for the operation to complete")
        return False
