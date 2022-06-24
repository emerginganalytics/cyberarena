from google.cloud import datastore

from utilities_v2.globals import DatastoreKeyTypes

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class DataStoreManager:
    def __init__(self, key_type=None, key_id=None):
        self.key_id = key_id
        self.ds_client = datastore.Client()
        if key_type:
            self.key = self.ds_client.key(key_type, key_id)
        else:
            self.key = None

    def get(self):
        return self.ds_client.get(self.key)

    def put(self, obj):
        ds_entity = datastore.Entity(key=self.key)
        ds_entity.update(obj)
        self.ds_client.put(ds_entity)

    def set(self, key_type, key_id):
        self.key_id = key_id
        self.key = self.ds_client.key(key_type, self.key_id)

    def get_servers(self):
        """ Get servers from workout"""
        query_servers = self.ds_client.query(kind=DatastoreKeyTypes.SERVER)
        query_servers.add_filter('workout', '=', self.key_id)
        return list(query_servers.fetch())

    def get_workouts(self):
        """Get workouts from unit"""
        query_workouts = self.ds_client.query(kind=DatastoreKeyTypes.CYBERGYM_WORKOUT)
        query_workouts.add_filter('unit_id', '=', self.key_id)
        return list(query_workouts.fetch())

    def get_classroom(self):
        query_classroom = self.ds_client.query(kind=DatastoreKeyTypes.CLASSROOM)
        query_classroom.add_filter('teacher_email', '=', self.key_id)
        return list(query_classroom.fetch())

    def get_injection(self):
        pass
