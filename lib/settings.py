import json, os, tempfile, time, platform, getpass, logging
import utils

# Replace any occurrence in obj of ${key} by its value, for each key in the
# dictionary.
def filter(obj, dictionary):
    if obj is None:
      return None
    elif isinstance(obj, str):
      for key, value in dictionary.items():
        obj = obj.replace('${%s}' % key, value)
      return obj
    elif isinstance(obj, unicode):
      return filter(str(obj), dictionary)
    elif isinstance(obj, bool):
      return obj
    elif isinstance(obj, dict):
      return dict([(k, filter(i, dictionary)) for (k, i) in obj.items()])
    elif hasattr(obj, '__iter__'):
      return map(lambda item: filter(item, dictionary), obj)
    else:
      raise Exception('Unknown obj type \'%s\'.' % type(obj))

class SettingsFileException(Exception):
    def __init__(self, subexception, filepath):
        self.subexception = subexception
        self.filepath = filepath

# Load a json file ignoring //-like comments.
def load_file(file_path):
    try:
      strip = lambda line: line[:line.find('//')].replace('\n', '')
      file_obj = open(file_path, 'r')
      lines = [line for line in map(strip, file_obj) if not line.isspace()]
      return json.loads(''.join(lines))
    except Exception as e:
      raise SettingsFileException(e, file_path)
    finally:
      file_obj.close()

class SettingsFileWatcher(object):
    def __init__(self, root, filter=None, include=[], exclude=[], sortkey=None, permanent={}):
        self.__getter = lambda: sorted(utils.find_files(root, include, exclude), sortkey)
        self.__data = {}
        self.__permanent = permanent
        if filter is not None:
          self.__filter = filter
        else:
          self.__filter = lambda obj: obj
        self.__mtime = None

    def get(self, key):
        self.__reload_if_needed()
        return self.__filter(self.__data.get(key))

    def getall(self):
        self.__reload_if_needed()
        return self.__filter(self.__data)

    def __reload_if_needed(self):
        if self.__mtime is None:
          self.__load(self.__getter())
          return
        files = self.__getter()
        for f in files:
          if os.stat(f).st_mtime > self.__mtime:
            self.__load(files)

    def __load(self, files):
        for f in files:
          try:
            self.__data.update(load_file(f))
          except SettingsFileException as e:
            print('Error on settings file \'%s\'' % e.filepath)
            print('%s: %s' % (type(e.subexception).__name__, e.subexception))
        self.__data.update(self.__permanent)
        self.__mtime = time.time()
