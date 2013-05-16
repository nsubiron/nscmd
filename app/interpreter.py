import logging, inspect, re
from lib import console, plugins

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def get_command_name(class_name):
    s1 = first_cap_re.sub(r'\1_\2', class_name.replace('Command', ''))
    return all_cap_re.sub(r'\1_\2', s1).lower()

def get_autocomplete(list_generator):
    def autocomplete_wrapper(c, text, line, start_index, end_index):
        if text:
          return [field for field in list_generator() if field.startswith(text)]
        return list_generator()
    return autocomplete_wrapper

class Interpreter(console.Shell):
    def __init__(self, prompt, plugin_generator):
        console.Shell.__init__(self, prompt)
        self.plugins = plugins.PluginManager(plugin_generator)
        self.addons = []
        self.do_reload_plugins()

    def do_reload_plugins(self, dummy=''):
        while len(self.addons) > 0:
          delattr(self.__class__, self.addons.pop())
        self.plugins.reload()
        for plugin in self.plugins:
          self.add_plugin(plugin)
        if len(self.plugins.invalids) > 0:
          print('Some plugins where not added, type \'plugin_errors\' for more info.')

    def do_plugin_errors(self, dummy=''):
        if len(self.plugins.invalids) > 0:
           print('The following plugins where not added:')
           for e in self.plugins.invalids:
             print('  %s: %s' % (e.name, e.reason))
        else:
          print('No errors found.')

    def setattr(self, name, value):
        setattr(self.__class__, name, value)
        self.addons.append(name)

    def add_plugin(self, plugin):
        name = get_command_name(plugin.name)
        if plugin.hasattr('run'):
          argc = len(plugin.getargs('run'))
          if argc == 0:
            cmd = lambda self, line: plugin.call('run')
          else:
            cmd = lambda self, line: plugin.call('run', [name] + line.split())
          self.setattr('do_%s' % name, cmd)
          if plugin.hasattr('complete'):
            self.setattr('complete_%s' % name, lambda self: plugin.call('complete'))
          elif plugin.hasattr('complete_list'):
            complete = get_autocomplete(lambda: plugin.call('complete_list'))
            self.setattr('complete_%s' % name, complete)
        if plugin.hasattr('help'):
          self.setattr('help_%s' % name, lambda self: plugin.call('help'))
        elif plugin.getdoc() is not None:
          def printdoc(self):
              print(plugin.getdoc())
          self.setattr('help_%s' % name, printdoc)
        elif plugin.hasattr('run') and plugin.getdoc('run') is not None:
          def printdoc(self):
              print(plugin.getdoc('run'))
          self.setattr('help_%s' % name, printdoc)
