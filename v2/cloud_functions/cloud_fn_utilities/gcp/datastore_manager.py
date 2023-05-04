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
    MAX_ATTEMPTS = 20
    WAIT_PERIOD = 3

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
            use_key = self.ds_client.key(key_type, key_id)
        else:
            use_key = self.key
        obj = self.ds_client.get(use_key)
        i = 0
        while not obj and i < self.MAX_ATTEMPTS and key_type != DatastoreKeyTypes.ADMIN_INFO:
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

    def put_multi(self, entities):
        self.ds_client.put_multi(entities=entities)

    def query(self, limit=None, **kwargs):
        """Returns query object"""
        if limit:
            return list(self.ds_client.query(kind=self.key_type, **kwargs).fetch(limit=limit))
        return list(self.ds_client.query(kind=self.key_type, **kwargs).fetch())

    def set(self, key_type, key_id):
        self.key_id = key_id
        self.key = self.ds_client.key(key_type, self.key_id)

    def entity(self, obj):
        """Returns Entity object"""
        ds_entity = datastore.Entity(self.key)
        ds_entity.update(obj)
        return self._create_safe_entity(ds_entity)

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
        if self.key_type in [DatastoreKeyTypes.FIXED_ARENA_CLASS, DatastoreKeyTypes.UNIT]:
            query_expired.add_filter('workspace_settings.expires', '<', get_current_timestamp_utc())
            for obj in query_expired.fetch():
                if obj.get('state', None) != FixedArenaClassStates.DELETED.value:
                    expired.append(obj.key.name)
        elif self.key_type == DatastoreKeyTypes.SERVER:
            query_expired.add_filter('shutoff_timestamp', '<', get_current_timestamp_utc())
            expired += list(query_expired.fetch())
        return expired

    def get_expiring_units(self):
        """
        returns a list of all the units that expire within 48 hours
        @return:
        """
        query_expiring = self.ds_client.query(kind=DatastoreKeyTypes.UNIT)
        two_days = 172800
        query_expiring.add_filter('workspace_settings.expires', '<', (get_current_timestamp_utc() + two_days))
        expiring = []
        for obj in query_expiring.fetch():
            if obj.get('state', None) != FixedArenaClassStates.DELETED.value:
                expiring.append(obj.key.name)
        return expiring

    def get_ready_for_shutoff(self):
        ready_for_shutoff = []
        query_shutoff = self.ds_client.query(kind=self.key_type)
        if self.key_type in [DatastoreKeyTypes.WORKOUT, DatastoreKeyTypes.FIXED_ARENA_CLASS]:
            query_shutoff.add_filter('shutoff_timestamp', '<', get_current_timestamp_utc())
            for obj in query_shutoff.fetch():
                if obj.get('shutoff_timestamp', None):
                    ready_for_shutoff.append(obj.key.name)
            return ready_for_shutoff
        else:
            self.logger.warning(f"Attempting to query labs ready for shutoff on an unsupported key type: "
                                f"{self.key_type}.")
            return []

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
            query_running.add_filter('state', '=', ServerStates.RUNNING.value)
            running += list(query_running.fetch())

        return running

    def get_admins(self):
        """Returns list of emails for admin accounts"""
        users = self.ds_client.query(kind=DatastoreKeyTypes.USERS).add_filter('permissions.admin', '=', True)
        return list(users.fetch())

    @staticmethod
    def _create_safe_entity(entity):
        exclude_from_indexes = []
        for item in entity:
            if type(entity[item]) == str and len(entity[item]) > 1500:
                exclude_from_indexes.append(item)
        entity.exclude_from_indexes = exclude_from_indexes
        return entity
