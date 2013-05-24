import json, os, time
import utils

class SettingsFileException(Exception):
    def __init__(self, subexception, filepath):
        self.subexception = subexception
        self.filepath = filepath

def load_file(file_path):
    """Load a json file ignoring //-like comments."""
    try:
      fileobj = None
      strip = lambda line: line[:line.find('//')].replace('\n', '')
      fileobj = open(file_path, 'r')
      lines = [line for line in map(strip, fileobj) if not line.isspace()]
      return json.loads(''.join(lines))
    except Exception as e:
      raise SettingsFileException(e, file_path)
    finally:
      if fileobj is not None:
        fileobj.close()

class SettingsFileWatcher(object):
    """Retrieve settings stored in json files. file_getter should be a callable
    object that generates a sorted set of json files, last files overwrite
    settings of previous files if duplicated. filter_function is used to filter
    the data before retrieve it."""
    def __init__(self, file_getter, filter_function=lambda x: x):
        self._getter = file_getter
        self._data = {}
        self._permanentdata = {}
        self._filter = filter_function
        self._mtime = 0

    def add_permanent_settings(self, data):
        """Data that will overwrite settings stored in files if duplicated."""
        self._data.update(data)
        self._permanentdata.update(data)

    def get(self):
        """Return a dictionary object with the data stored in the files."""
        self._reload()
        return self._filter(self._data)

    def _reload(self):
        load = False
        for f in self._getter():
          try:
            if os.stat(f).st_mtime > self._mtime:
              load = True
            if load:
              self._data.update(load_file(f))
          except SettingsFileException as e:
            print('Error on settings file \'%s\'' % e.filepath)
            print('%s: %s' % (type(e.subexception).__name__, e.subexception))
        self._data.update(self._permanentdata)
        self._mtime = time.time()
