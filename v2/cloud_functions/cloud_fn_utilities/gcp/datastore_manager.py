import time

from google.cloud import datastore
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError

from cloud_fn_utilities.globals import DatastoreKeyTypes, get_current_timestamp_utc, ServerStates, FixedArenaClassStates
from cloud_fn_utilities.gcp.cloud_logger import Logger

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class DataStoreManager:
    def __init__(self, key_type=None, key_id=None):
        self.logger = Logger("cloud_functions.compute_manager").logger
        self.key_type = key_type
        self.key_id = key_id
        try:
            self.ds_client = datastore.Client()
        except HttpError as e:
            self.logger.warning(f"Error getting datastore client connection. Backing off 5 seconds and trying again")
            time.sleep(5)
            self.ds_client = datastore.Client()
        if self.key_type and self.key_id:
            self.key = self.ds_client.key(self.key_type, self.key_id)
        else:
            self.key = None

    def get(self, key_type=None, key_id=None):
        if key_type:
            temp_key = self.ds_client.key(key_type, key_id)
            return self.ds_client.get(temp_key)
        else:
            return self.ds_client.get(self.key)

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

    def query(self, filter_key=None, op=None, value=None):
        """Returns query object"""
        if filter_key and op and value:
            query = self.ds_client.query(kind=self.key_id)
            query.add_filter(filter_key, f"{op}", value)
            return list(query.fetch())
        return self.ds_client.query(kind=self.key_id)

    def set(self, key_type, key_id):
        self.key_id = key_id
        self.key = self.ds_client.key(key_type, self.key_id)

    def get_servers(self):
        query_servers = self.ds_client.query(kind=DatastoreKeyTypes.SERVER)
        query_servers.add_filter('parent_id', '=', self.key_id)
        return list(query_servers.fetch())

    def get_children(self, child_key_type, parent_id):
        query_workspaces = self.ds_client.query(kind=child_key_type)
        query_workspaces.add_filter('parent_id', '=', parent_id)
        return list(query_workspaces.fetch())

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

    def get_running(self):
        """
        returns a list of running entities associated with the key_type
        @return:
        """
        running = []
        query_running = self.ds_client.query(kind=self.key_type)
        if self.key_type == DatastoreKeyTypes.FIXED_ARENA_CLASS:
            query_running.add_filter('state', '=', FixedArenaClassStates.RUNNING.value)
            running += list(query_running.fetch())
        elif self.key_type == DatastoreKeyTypes.SERVER:
            query_running.add_filter('state', '=', ServerStates.EXPIRED.value)
            running += list(query_running.fetch())

        return running

    @staticmethod
    def _create_safe_entity(entity):
        exclude_from_indexes = []
        for item in entity:
            if type(entity[item]) == str and len(entity[item]) > 1500:
                exclude_from_indexes.append(item)
        entity.exclude_from_indexes = exclude_from_indexes
        return entity
