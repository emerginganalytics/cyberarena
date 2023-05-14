from google.cloud import datastore

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
        self.key_type = key_type
        self.key_id = key_id
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
            self.ds_client.put(self.entity(obj))

    def put_multi(self, entities):
        self.ds_client.put_multi(entities=entities)

    def set(self, key_type, key_id):
        self.key_id = key_id
        self.key = self.ds_client.key(key_type, self.key_id)

    def query(self, limit=None, **kwargs):
        """Returns query object"""
        if limit:
            return list(self.ds_client.query(kind=self.key_type, **kwargs).fetch(limit=int(limit)))
        return list(self.ds_client.query(kind=self.key_type, **kwargs).fetch())

    def entity(self, obj):
        ds_entity = datastore.Entity(self.key)
        ds_entity.update(obj)
        return self._create_safe_entity(ds_entity)

    def get_children(self, child_key_type, parent_id):
        query_workspaces = self.ds_client.query(kind=child_key_type)
        query_workspaces.add_filter('parent_id', '=', parent_id)
        return list(query_workspaces.fetch())

    @staticmethod
    def _create_safe_entity(entity):
        exclude_from_indexes = []
        for item in entity:
            if type(entity[item]) == str and len(entity[item]) > 1500:
                exclude_from_indexes.append(item)
        entity.exclude_from_indexes = exclude_from_indexes
        return entity
