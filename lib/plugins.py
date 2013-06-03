import os, imp, inspect, sys, logging, utils, platform

PLATFORM = platform.system().lower()

class InvalidPlugin(Exception):
    def __init__(self, plugin, reason):
        Exception.__init__(self, '%s: %s' % (plugin.name, reason))
        self.plugin = plugin
        self.name = plugin.name
        self.reason = reason

class PluginProxy(object):
    def __init__(self, name, declaration):
        self.name = name
        self.declaration = declaration
        self.instance = None

    def validate(self):
        try:
          if hasattr(self.declaration, '__platforms__'):
            if all(p.lower() != PLATFORM for p in self.declaration.__platforms__):
              raise InvalidPlugin(self, 'Platform not supported.')
          if hasattr(self.declaration, '__extdependencies__'):
            if any(utils.which(d) is None for d in self.declaration.__extdependencies__):
              raise InvalidPlugin(self, 'One or more dependencies not installed.')
        except InvalidPlugin as e:
          raise e
        except Exception as e:
          message = 'Exception raised during validation: %s: %s'
          raise InvalidPlugin(self, message % (type(e).__name__, e))

    def instantiate(self, *args, **kwargs):
        try:
          self.instance = self.declaration(*args, **kwargs)
        except Exception as e:
          message = 'Exception raised creating instance: %s: %s'
          raise InvalidPlugin(self, message % (type(e).__name__, e))

    def hasattr(self, name):
        return hasattr(self.instance, name)

    def getattr(self, name, default=None):
        try:
          if self.instance is not None:
            return getattr(self.instance, name)
          return getattr(self.declaration, name)
        except:
          return default

    def getdoc(self, name=None):
        if name is None:
          return self.instance.__doc__
        return self.getattr(name).__doc__

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
    strip_ext = lambda f: os.path.splitext(os.path.basename(f))[0]
    is_valid = lambda obj: inspect.isclass(obj) and issubclass(obj, interface)
    for directory in directories:
      for dirname, _, filenames in utils.walk(directory, ['*.py','*.pyc']):
        added = False
        if dirname not in sys.path:
          sys.path.insert(0, dirname)
          added = True
        for module_name in set(strip_ext(f) for f in filenames):
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
