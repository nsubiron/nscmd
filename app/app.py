import os, sys, inspect, types, platform, logging, argparse
from lib import utils, settings, truecrypt, prompt, plugins
import interpreter

__all__ = ['main']

CALLERDIR = os.getcwd()

## os ##########################################################################

def get_this_folder():
    f = inspect.getfile(inspect.currentframe())
    return os.path.realpath(os.path.abspath(os.path.split(f)[0]))

def add_to_path(paths):
    for path in [ p for p in paths if os.path.isdir(p) ]:
      if path not in os.environ['PATH']:
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + path

## init environment ############################################################

def init_nscmd_module(args):
    module = sys.modules['nscmd'] = types.ModuleType('nscmd')
    module.APPNAME = 'nscmd'
    module.ROOT = os.path.split(get_this_folder())[0]
    module.PLATFORM = platform.system().lower()
    sysmap = {'root': module.ROOT}
    sysmap['home'] = os.path.expanduser('~')
    module.filter = lambda obj: settings.filter(obj, sysmap)
    settings_folder = os.path.join(module.ROOT, 'settings')
    excludes = ['linux', 'windows']
    excludes.remove(module.PLATFORM)
    sfw = settings.SettingsFileWatcher(
        settings_folder,
        filter=module.filter,
        permanent=args,
        include=['*.ns-settings'],
        exclude=map(lambda item : item + '.ns-settings', excludes))
    sysmap['vol'] = str(sfw.get('vol'))
    module.get_settings = lambda: sfw.getall()
    return module

def init_plugin_module():
    module = sys.modules['nsplugin'] = types.ModuleType('nsplugin')
    class AppCommand(object):
        pass
    module.AppCommand = AppCommand
    return module

def init_truecrypt(volume, where):
    if utils.which(truecrypt.APP) is None:
      print('%s not found.' % truecrypt.APP)
      return None
    if volume is None or where is None:
      return None
    if not os.path.isfile(str(volume)):
      print('Volume file \'%s\' not found.' % volume)
      return None
    if prompt.yes_no('Mount volume?', 'yes'):
      try:
        return truecrypt.TruecryptWrapper(volume, where)
      except truecrypt.TruecryptException:
        pass
    return None

## main ########################################################################

def parse_arguments():
    parser = argparse.ArgumentParser(prog='nscmd')
    parser.add_argument('--volume', help='specify volume file')
    parser.add_argument('--vol', help='specify mounting point for the volume file')
    parser.add_argument('--path', nargs='+', default=[], help='add to environment variable PATH')
    return dict((k,v) for k,v in vars(parser.parse_args()).items() if v is not None)

def main():
    try:
      args = parse_arguments()
      add_to_path(args.pop('path'))
      print('Starting nscmd ...')
      nscmd = init_nscmd_module(args)
      nsplugin = init_plugin_module()
      sett = nscmd.get_settings()
      tcwrapper = init_truecrypt(sett.get('volume'), sett.get('vol'))
      starting_dir = str(sett.get('starting_dir', nscmd.filter('${vol}')))
      if os.path.isdir(starting_dir):
        os.chdir(starting_dir)
      plugins_folder = os.path.join(nscmd.ROOT, 'plugins')
      plugin_generator = lambda: plugins.load_plugins(plugins_folder, nsplugin.AppCommand)
      cmd = interpreter.Interpreter('ns', plugin_generator)
      cmd.cmdloop()
    except (SystemExit, KeyboardInterrupt):
      print
    except:
      logging.exception('Uncaught exception.')
      pass
    finally:
      if tcwrapper is not None:
        os.chdir(CALLERDIR)
        tcwrapper.dismount()
