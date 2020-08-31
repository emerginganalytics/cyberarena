import googleapiclient.discovery
from googleapiclient.errors import HttpError
from socket import timeout

from common.globals import project, zone


def create_snapshot_from_disk(disk):
    """
    This function keeps at most 2 snapshot available from a server
    param disk: The name of the server
    return: Either the name of the new snapshot or None
    """
    service = googleapiclient.discovery.build('compute', 'v1')

    i = 0
    found_available = False
    while i < 3 and not found_available:
        try:
            response = service.snapshots().get(project=project, snapshot=disk + str(i)).execute()
            i += 1
        except HttpError:
            found_available = True
    if not found_available:
        i = i - 1

    snapshot_to_delete = disk + str((i + 1) % 3)
    try:
        response = service.snapshots().delete(project=project, snapshot=snapshot_to_delete).execute
    except HttpError:
        pass

    snapshot_to_create = disk + str(i)
    snapshot_body = {
        'name': snapshot_to_create,
        'description': 'Production snapshot used for imaging'
    }

    response = service.disks().createSnapshot(project=project, zone=zone, disk=disk, body=snapshot_body).execute()
    i = 0
    success = False
    while not success and i < 5:
        try:
            print(f"Begin waiting for snapshot creation {response['id']}")
            response = service.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            print('Response timeout for production snapshot. Trying again')
            pass

    if not success:
        return None
    else:
        return snapshot_to_create


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
        build_success = False
        nothing_to_delete = False
        while not build_success and i < 5 and not nothing_to_delete:
            try:
                response = service.images().delete(project=project, image=prod_image).execute()
                build_success = True
                print(f'Sent job to delete the production image before creating a new one, and waiting for response')
            except HttpError:
                nothing_to_delete = True
            except BrokenPipeError:
                i += 1
        i = 0
        success = False
        while not success and i < 5 and not nothing_to_delete:
            try:
                print(f"Begin waiting for image deletion operation {response['id']}")
                service.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
                success = True
            except timeout:
                i += 1
                print('Response timeout for production image deletion. Trying again')
                pass

        if success or nothing_to_delete:
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
                    print(
                        f'Sent job to create the new production image, and waiting for response')
                except BrokenPipeError:
                    i += 1
            return True
        else:
            print(f"Error in publishing production image. Timeout waiting for the operation to complete")
            return False

create_production_image('cybergym-mobileforensics')