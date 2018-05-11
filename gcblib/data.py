#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license

import hashlib
import json
import os


class DataStore():
    """Stores and manages data."""
    top_version = 1

    def __init__(self, path):
        self.path = path
        self.store = {}
        self.load()

    # loading and saving
    def load(self):
        """Load information from our data file."""
        try:
            with open(self.path, 'r') as info_file:
                self.store = json.loads(info_file.read())
                current_version = self.store.get('store_version', 1)
                while current_version < self.top_version:
                    current_version = self.update_store_version(current_version)
        except FileNotFoundError:
            self.initialize_store()

    def save(self):
        """Save information to our data file."""
        # only save file if we have data
        if not self.store:
            return

        # ensure info file folder exists
        folder = os.path.dirname(self.path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

        with open(self.path, 'w') as info_file:
            info_file.write(json.dumps(self.store, sort_keys=True, indent=4))

    # version updating
    def initialize_store(self):
        """Initialize the info store."""
        self.store = {
            'store_version': self.top_version,
        }

    def update_store_version(self, current_version):
        """Update our internal store from the given verison, return the new version."""
        raise NotImplementedError('update_store_version must be replaced when subclassed')

    # helper function
    def _split_base_from_key(self, key):
        if isinstance(key, (list, tuple)):
            base = self.store
            for key_part in key[:-1]:
                if key_part not in base:
                    return None, None
                base = base[key_part]
            key = key[-1]
        else:
            base = self.store

        return base, key

    def _create_base_from_key(self, key):
        if isinstance(key, (list, tuple)):
            base = self.store
            for key_part in key[:-1]:
                if key_part not in base:
                    base[key_part] = {}
                base = base[key_part]

    # getting and setting
    def has_key(self, key):
        """Returns True if we have the given key in our store."""
        base, key = self._split_base_from_key(key)
        if base is None:
            return False

        return key in base

    def has_all_keys(self, *keys):
        """Returns True if we have all of the given keys in our store."""
        for key in keys:
            if not self.has_key(key):
                return False
        return True

    def set(self, key, value, create_base=True):
        """Sets key to value in our store."""
        # find base
        if isinstance(key, (list, tuple)):
            base = self.store
            for key_part in key[:-1]:
                if key_part not in base:
                    if create_base:
                        base[key_part] = {}
                    else:
                        raise Exception('key_part not in base: {}'.format(key))
                base = base[key_part]
            key = key[-1]
        else:
            base = self.store

        base[key] = value
        self.save()

    def get(self, key, default=None):
        """Returns value from our store, or default if it doesn't exist."""
        base, key = self._split_base_from_key(key)
        if base is None:
            return default

        return base.get(key, default)

    def remove(self, key):
        """Remove the given key from our store."""
        if not self.has_key(key):
            return

        # find base
        if isinstance(key, (list, tuple)):
            base = self.store
            for key_part in key[:-1]:
                if key_part not in base:
                    # XXX - TODO: - wtf to do here?
                    if False:#create_base:
                        base[key_part] = {}
                    else:
                        raise Exception('key_part not in base: {}'.format(key))
                base = base[key_part]
            key = key[-1]
        else:
            base = self.store

        try:
            del base[key]
        except KeyError:
            pass

        self.save()

    def initialize_to(self, key, value):
        """If key is not in our store, set it to value."""
        if self.has_key(key):
            return

        self.set(key, value)

    def append_to(self, key, value):
        """Append a value to a list in our store."""
        # find base
        if isinstance(key, (list, tuple)):
            base = self.store
            for key_part in key[:-1]:
                if key_part not in base:
                    # XXX - TODO: - wtf to do here?
                    if False:#create_base:
                        base[key_part] = {}
                    else:
                        raise Exception('key_part not in base: {}'.format(key))
                base = base[key_part]
            key = key[-1]
        else:
            base = self.store

        base[key].append(value)

        self.save()

    def remove_from(self, key, value):
        """Remove a value from a list in our store."""
        # find base
        if isinstance(key, (list, tuple)):
            base = self.store
            for key_part in key[:-1]:
                if key_part not in base:
                    # XXX - TODO: - wtf to do here?
                    if False:#create_base:
                        base[key_part] = {}
                    else:
                        raise Exception('key_part not in base: {}'.format(key))
                base = base[key_part]
            key = key[-1]
        else:
            base = self.store

        base[key].remove(value)

        self.save()
