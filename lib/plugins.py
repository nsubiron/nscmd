import re, os, fnmatch, imp, inspect, sys, logging

class PluginError(Exception):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, name)

class PluginProxy(object):
    def __init__(self, name, declaration):
        self.name = name
        self.declaration = declaration

    def instantiate(self, *args, **kwargs):
        try:
          self.instance = self.declaration(*args, **kwargs)
        except:
          logging.exception('Exception creating instance of plugin \'%s\'' % self.name)
          raise PluginError(self.name)

    def hasattr(self, name):
        return hasattr(self.instance, name)

    def getargs(self, name):
        try:
          f = getattr(self.instance, name)
          return [x for x in inspect.getargspec(f).args if x != 'self']
        except:
          logging.exception('Exception getting \'%s.%s\'' % (self.name, name))

    def call(self, _name, *args, **kwargs):
        try:
          return getattr(self.instance, _name)(*args, **kwargs)
        except:
          logging.exception('Exception calling \'%s.%s\'' % (self.name, _name))

class PluginManager(object):
    def __init__(self, generator):
        self.generator = generator
        self.plugins = []

    def __iter__(self):
        return self.plugins.__iter__()

    def clear(self):
        del self.plugins[0:len(self.plugins)]

    def reload(self):
        self.clear()
        for plugin in self.generator():
          try:
            plugin.instantiate()
            self.plugins.append(plugin)
          except PluginError:
            pass

def load_plugins(directory, interface):
    directory = os.path.abspath(directory)
    module_pattern = re.compile('|'.join(fnmatch.translate(p) for p in ['*.py','*.pyc']))
    strip_ext = lambda f: os.path.splitext(os.path.basename(f))[0]
    get_modules = lambda files: set(strip_ext(f) for f in files if module_pattern.match(f))
    is_valid = lambda obj: inspect.isclass(obj) and issubclass(obj, interface)
    for dirname, _, filenames in os.walk(directory):
      added = False
      if dirname not in sys.path:
        sys.path.insert(0, dirname)
        added = True
      for module_name in get_modules(filenames):
        try:
          module_info = imp.find_module(module_name, [dirname])
          # This do a reload if already imported.
          module = imp.load_module(module_name, *module_info)
          for name, declaration in inspect.getmembers(module, is_valid):
            yield PluginProxy(name, declaration)
        except:
          pass
        finally:
          module_info[0].close()
      if added:
        sys.path.remove(dirname)
