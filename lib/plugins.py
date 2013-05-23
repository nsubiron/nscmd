import re, os, fnmatch, imp, inspect, sys, logging, utils, platform

PLATFORM = platform.system().lower()

class InvalidPlugin(Exception):
    def __init__(self, name, reason):
        Exception.__init__(self, name)
        self.name = name
        self.reason = reason

class PluginProxy(object):
    def __init__(self, name, declaration):
        self.name = name
        self.declaration = declaration

    def validate(self):
        try:
          if hasattr(self.declaration, '__platforms__'):
            if all(p.lower() != PLATFORM for p in self.declaration.__platforms__):
              raise InvalidPlugin(self.name, 'Platform not supported.')
          if hasattr(self.declaration, '__extdependencies__'):
            if any(utils.which(d) is None for d in self.declaration.__extdependencies__):
              raise InvalidPlugin(self.name, 'One or more dependencies not installed.')
        except InvalidPlugin as e:
          raise e
        except Exception as e:
          message = 'Exception raised during validation: %s: %s'
          raise InvalidPlugin(self.name, message % (type(e).__name__, e))

    def instantiate(self, *args, **kwargs):
        try:
          self.instance = self.declaration(*args, **kwargs)
        except Exception as e:
          logging.exception('Exception creating instance of plugin \'%s\'' % self.name)
          message = 'Exception raised creating instance: %s: %s'
          raise InvalidPlugin(self.name, message % (type(e).__name__, e))

    def hasattr(self, name):
        return hasattr(self.instance, name)

    def getdoc(self, name=None):
        if name is None:
          return self.instance.__doc__
        else:
          try:
            return getattr(self.instance, name).__doc__
          except:
            logging.exception('Exception getting \'%s.%s\'' % (self.name, name))

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
        self.invalids = []

    def __iter__(self):
        return self.plugins.__iter__()

    def clear(self):
        del self.plugins[0:len(self.plugins)]
        del self.invalids[0:len(self.invalids)]

    def reload(self):
        self.clear()
        for plugin in self.generator():
          try:
            plugin.validate()
            plugin.instantiate()
            self.plugins.append(plugin)
          except InvalidPlugin as e:
            self.invalids.append(e)

def load_plugins(directories, interface):
    module_pattern = re.compile('|'.join(fnmatch.translate(p) for p in ['*.py','*.pyc']))
    strip_ext = lambda f: os.path.splitext(os.path.basename(f))[0]
    get_modules = lambda files: set(strip_ext(f) for f in files if module_pattern.match(f))
    is_valid = lambda obj: inspect.isclass(obj) and issubclass(obj, interface)
    for directory in directories:
      for dirname, subfolders, filenames in os.walk(os.path.abspath(directory)):
        subfolders[:] = [d for d in subfolders if not d[0] == '.']
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
