import time

from google.cloud import datastore
from main_app_utilities.globals import DatastoreKeyTypes, ServerStates, get_current_timestamp_utc
from google.cloud import logging_v2

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class DataStoreManager:
    MAX_ATTEMPTS = 5
    WAIT_PERIOD = 3

    def __init__(self, key_type=None, key_id=None):
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.key_type = key_type
        self.key_id = key_id
        self.ds_client = datastore.Client()
        if self.key_type and self.key_id:
            self.key = self.ds_client.key(self.key_type, self.key_id)
        else:
            self.key = None

    def get(self, key_type=None, key_id=None):
        if key_type:
            use_key = self.ds_client.key(key_type, key_id)
        else:
            use_key = self.key
        obj = self.ds_client.get(use_key)
        i = 0
        while not obj and i < self.MAX_ATTEMPTS:
            i += 1
            time.sleep(self.WAIT_PERIOD)
            obj = self.ds_client.get(use_key)
        return obj

    def put(self, obj, key_type=None, key_id=None):
        if key_type:
            self.key = self.ds_client.key(key_type, key_id)
        try:
            obj.key = self.key
            self.ds_client.put(self._create_safe_entity(obj))
        except AttributeError:
            # An attribute error occurs when passing in a dictionary. In this case, create a new entity from the dict
            ds_entity = datastore.Entity(self.key)
            ds_entity.update(obj)
            self.ds_client.put(self._create_safe_entity(ds_entity))

    def set(self, key_type, key_id):
        self.key_id = key_id
        self.key = self.ds_client.key(key_type, self.key_id)

    def query(self, filter_key=None, op=None, value=None):
        """Returns query object"""
        if filter_key and op and value:
            query = self.ds_client.query(kind=self.key_id)
            query.add_filter(filter_key, f"{op}", value)
            return list(query.fetch())
        return self.ds_client.query(kind=self.key_id)

    def delete(self):
        self.ds_client.delete(self.key)

    def get_servers(self):
        query_servers = self.ds_client.query(kind=DatastoreKeyTypes.SERVER)
        query_servers.add_filter('parent_id', '=', self.key_id)
        return list(query_servers.fetch())

    def get_children(self, child_key_type, parent_id):
        query_workspaces = self.ds_client.query(kind=child_key_type)
        query_workspaces.add_filter('parent_id', '=', parent_id)
        children = list(query_workspaces.fetch())
        i = 0
        while not children and i < self.MAX_ATTEMPTS:
            i += 1
            time.sleep(self.WAIT_PERIOD)
            children = list(query_workspaces.fetch())
        return children

    def get_expired(self):
        expired = []
        query_expired = self.ds_client.query(kind=self.key_type)
        if self.key_type == DatastoreKeyTypes.FIXED_ARENA_CLASS:
            query_expired.add_filter('workspace_settings.expires', '<', get_current_timestamp_utc())
            expired += list(query_expired.fetch())
        elif self.key_type == DatastoreKeyTypes.SERVER:
            query_expired.add_filter('state', '=', ServerStates.EXPIRED.value)
            expired += list(query_expired.fetch())

        return expired

    def get_classrooms(self, class_name=None):
        """Queries for corresponding cybergym-class"""
        query_classroom = self.ds_client.query(kind=DatastoreKeyTypes.CLASSROOM.value)
        query_classroom.add_filter('teacher_email', '=', self.key_id)
        if class_name:
            query_classroom.add_filter('class_name', '=', str(class_name))
        return list(query_classroom.fetch())

    @staticmethod
    def _create_safe_entity(entity):
        exclude_from_indexes = []
        for item in entity:
            if type(entity[item]) == str and len(entity[item]) > 1500:
                exclude_from_indexes.append(item)
        entity.exclude_from_indexes = exclude_from_indexes
        return entity
