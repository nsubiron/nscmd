import platform, os, argparse, re, time
import utils, settings

def get_commands(platform=platform.system()):
    args = {}
    if platform.lower() == 'windows':
      args['automount'] = '${app} /q /v ${volume}'
      args['mount'] = '${app} /q /v ${volume} /l${where}'
      args['dismount'] = '${app} /q /d${where}'
      args['dismountall'] = '${app} /q'
    else:
      args['automount'] = 'sudo ${app} -t -k "" --protect-hidden=no ${volume}'
      args['mount'] = 'sudo ${app} -t -k "" --protect-hidden=no ${volume} ${where}'
      args['dismount'] = 'sudo ${app} -t -d ${where}'
      args['dismountall'] = 'sudo ${app} -t -d'
    return args

APP = 'truecrypt'

COMMANDS = get_commands()

def out(text):
    print(text)

def mount(volume, where, validator=os.path.isdir, timeout=15):
    dictionary = { 'app': APP, 'volume': volume, 'where': where }
    out(settings.filter('Mounting ${volume} at ${where} ...', dictionary))
    os.system(settings.filter(COMMANDS['mount'], dictionary))
    return wait(where, validator, timeout)

def automount(volume):
    dictionary = { 'app': APP, 'volume': volume }
    out(settings.filter('Mounting ${volume} ...', dictionary))
    os.system(settings.filter(COMMANDS['automount'], dictionary))

def dismount(where):
    dictionary = { 'app': APP, 'where': where }
    out(settings.filter('Dismounting ${where} ...', dictionary))
    os.system(settings.filter(COMMANDS['dismount'], dictionary))

def dismountall():
    dictionary = { 'app': APP }
    out('Dismounting all ...')
    os.system(settings.filter(COMMANDS['dismountall'], dictionary))

def call(argv):
    parser = argparse.ArgumentParser(prog='truecrypt')
    class ExitException(Exception):
        pass
    def doexit(status=0, message=None):
        if message is not None:
          print(message)
        raise ExitException
    parser.exit = doexit
    subparsers = parser.add_subparsers(dest='cmd')
    for key, cmd in COMMANDS.items():
      subparser = subparsers.add_parser(key)
      for arg in re.findall(r"\$\{([A-Za-z0-9_]+)\}", cmd)[1:]:
        subparser.add_argument(arg)
    try:
      args = vars(parser.parse_args(argv))
    except (ExitException, SystemExit):
      return
    cmd = args.pop('cmd')
    args['app'] = APP
    os.system(settings.filter(COMMANDS[cmd], args))

def wait(mount_point, validator, time_out, time_step=1):
    if validator(mount_point):
      return True
    try:
      print('Waiting for truecrypt ...')
      start = time.time()
      while True:
        if validator(mount_point):
          return True
        if (time.time() - start) > time_out:
          break
        time.sleep(time_step)
      return False
    except KeyboardInterrupt:
      return False

class TruecryptException(Exception):
    pass

class TruecryptWrapper(object):
    def __init__(self, volume, where):
        if not mount(str(volume), str(where)):
          raise TruecryptException('Error mounting %s at %s.' % (volume, where))
        self.dismount = lambda: dismount(where)
        self.__del__ = lambda: dismount(where)
