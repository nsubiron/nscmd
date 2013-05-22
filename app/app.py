"""
  nscmd is licensed under the GPL license.

  Copyright (C) 2013 N. Subiron

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
import os, sys, inspect, types, platform, logging, argparse
from lib import utils, settings, truecrypt, prompt, plugins
import interpreter

__all__ = ['main', 'LICENSE']

CALLERDIR = os.getcwd()

LICENSE = __doc__

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
    sysmap['data_dir'] = str(sfw.get('data_dir'))
    module.get_settings = lambda: sfw.getall()
    return module

def init_plugin_module():
    module = sys.modules['nsplugin'] = types.ModuleType('nsplugin')
    class AppCommand(object):
        """Base class for plugin classes."""
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
      tcw = None
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
      plugin_dirs = sett.get('plugin_dirs', [])
      plugin_generator = lambda: plugins.load_plugins(plugin_dirs, nsplugin.AppCommand)
      ignore_list = sett.get('ignore_list', [])
      cmd = interpreter.Interpreter('ns', plugin_generator, ignore_list)
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
