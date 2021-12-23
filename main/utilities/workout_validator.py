from googleapiclient.errors import HttpError
from utilities.globals import compute, logger, project, storage_client, workout_globals, cloud_log, LogIDs, LOG_LEVELS


class WorkoutValidator:
    """
    Validation class to help prevent any build errors from occurring due to missing
    resources in project.
    """
    def __init__(self, image_list=None, workout_type=None):
        self.image_list = image_list
        self.workout_type = workout_type

    def validate_machine_images(self):
        """
        Args:
            self.image_list: List of images used in workout
        Returns: Dict of status and error message. Status is False if at least one image
                 doesn't exist for that project.
        """
        if self.image_list:
            images_state = {
                'status': True,
                'bad_images': [],
            }
            for image in self.image_list:
                try:
                    compute.images().get(project=project, image=image).execute()
                except HttpError as e:
                    # Image doesn't exist; append bad image to list and log event
                    images_state['bad_images'].append(image)
                    logger.error('%s' % e.error_details[0]["message"])
            # Images in image_list doesn't exist in current project
            if len(images_state['bad_images']) > 0:
                error_message = f"Compute images not found! The following compute images do not exist in the " \
                                f"cloud project: {images_state['bad_images']}"
                cloud_log(LogIDs.MAIN_APP, error_message, LOG_LEVELS.ERROR)
                raise self.ImageNotFound(error_message)
            # All images exist in current project
            return images_state

    def yaml_check(self):
        """
        Checks for existence of YAML file in Cloud storage.
        Returns: True iff YAML with workout_type exists
        """
        if self.workout_type:
            workout_exists = False
            yaml_bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
            bucket = storage_client.get_bucket(yaml_bucket)
            for blob in bucket.list_blobs():
                if blob.name == ("yaml-build-files/" + self.workout_type + ".yaml"):
                    workout_exists = True
            return workout_exists

    class Error(Exception):
        """Base class for exceptions in this module."""
        pass

    class ImageNotFound(Error):
        """Exception raised for errors in the input.

        Attributes:
            expression -- input expression in which the error occurred
            message -- explanation of the error
        """
        def __init__(self, message):
            self.message = message
