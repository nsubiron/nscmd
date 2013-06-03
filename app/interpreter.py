import logging, inspect, re, shlex, app
from lib import console, plugins
import nsplugin

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

class PluginCommand(nsplugin.AppCommand):
    """plugin usage:
  plugin reload       - Delete current plugins, reload files and instantiate plugin classes.
  plugin errors       - Print errors found while loading plugins.
  plugin dependencies - Print external dependencies for each plugin.
  plugin platforms    - Print platform specifications for each plugin.
    """
    def __init__(self, parent, manager):
        self.parent = parent
        self.manager = manager
        self.attribs = {
            'dependencies': ['__extdependencies__', []],
            'platforms': ['__platforms__', ['not specified']]}

    def run(self, argv):
        cmd = argv[-1]
        if cmd == 'reload':
          self.parent.reload_plugins()
          if len(self.manager.invalids) > 0:
            print('Some plugins where not added, type \'plugin errors\' for more info.')
        elif cmd in self.attribs:
          get = lambda p: (get_command_name(p.name), p.getattr(*self.attribs[cmd]))
          d = dict(get(i.plugin) for i in self.manager.invalids)
          d.update(dict(get(p) for p in self.manager))
          maximum = max(map(len,d.keys()))
          for key in sorted(d.keys()):
            print('  %s = %s' % (key.ljust(maximum), ', '.join(d[key])))
        elif cmd == 'errors':
          if len(self.manager.invalids) > 0:
            print('The following plugins where not added:')
            for e in self.manager.invalids:
              print('  %s: %s' % (e.name, e.reason))
          else:
            print('No errors found.')
        else:
          print(PluginCommand.__doc__)

    def complete_list(self):
        return sorted(['reload', 'errors'] + self.attribs.keys())

class Interpreter(console.Shell):
    def __init__(self, prompt, plugin_generator, ignore_list):
        console.Shell.__init__(self, prompt)
        self.ignore_list = ignore_list
        self.plugins = plugins.PluginManager(plugin_generator)
        self.addons = []
        try:
          p = plugins.PluginProxy('PluginCommand', PluginCommand)
          p.validate()
          p.instantiate(self, self.plugins)
          self.add_plugin(p, permanent=True)
        except:
          logging.exception('Problem initializing \'plugin\' command.')
        self.reload_plugins()

    def run_command(self, line):
        try:
          args = line.split(' ', 1)
          default = lambda x: self.default(line)
          getattr(self, 'do_%s' % args[0], default)(' '.join(args[1:]))
        except:
          logging.exception('Exception running \'%s\'' % line)

    def reload_plugins(self):
        while len(self.addons) > 0:
          delattr(self.__class__, self.addons.pop())
        self.plugins.reload()
        for plugin in self.plugins:
          self.add_plugin(plugin)

    def do_license(self, dummy=''):
        print(app.LICENSE)
    help_license = do_license

    def setattr(self, name, value, permanent):
        setattr(self.__class__, name, value)
        if not permanent:
          self.addons.append(name)

    def add_plugin(self, plugin, permanent=False):
        name = get_command_name(plugin.name)
        if name in self.ignore_list:
          return
        if plugin.hasattr('run'):
          argc = len(plugin.getargs('run'))
          if argc == 0:
            cmd = lambda self, line: plugin.call('run')
          else:
            cmd = lambda self, line: plugin.call('run', [name] + shlex.split(line))
          self.setattr('do_%s' % name, cmd, permanent)
          if plugin.hasattr('complete'):
            complete_wrapper = lambda self: plugin.call('complete')
            self.setattr('complete_%s' % name, complete_wrapper, permanent)
          elif plugin.hasattr('complete_list'):
            complete = get_autocomplete(lambda: plugin.call('complete_list'))
            self.setattr('complete_%s' % name, complete, permanent)
        if plugin.hasattr('help'):
          help_wrapper = lambda self: plugin.call('help')
          self.setattr('help_%s' % name, help_wrapper, permanent)
        elif plugin.getdoc() is not None:
          def printdoc(self):
              print(plugin.getdoc())
          self.setattr('help_%s' % name, printdoc, permanent)
        elif plugin.hasattr('run') and plugin.getdoc('run') is not None:
          def printdoc(self):
              print(plugin.getdoc('run'))
          self.setattr('help_%s' % name, printdoc, permanent)
