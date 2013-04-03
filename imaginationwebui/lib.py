import json
import copy

from acidfs import AcidFS


class SlidesDataStore(object):

    def __init__(self, repository, filepath='slides.json'):
        self.filepath = filepath
        self._afs = AcidFS(repository)
        self._data = self._read()
        # if afs.session is not closed, the next transaction won't be bound
        # to the AcidFS datastore
        self._afs.session.close()


    def get(self):
        return copy.deepcopy(self._data)

    def set(self, data):
        # TODO: check that data really needs to be updated
        self._data = copy.deepcopy(data)
        self._write(data)

    def _read(self):
        data = {}
        if self._afs.exists(self.filepath):
            with self._afs.open(self.filepath, 'r') as f:
                data = json.load(f)
        return data

    def _write(self, data):
        with self._afs.open(self.filepath, 'wb') as f:
            json.dump(data, f, indent=4, sort_keys=True)
