import platform, os, argparse, re, time
import utils

def get_commands(platform=platform.system()):
    args = {}
    if platform.lower() == 'windows':
      args['automount'] = '${app} /q /v \"${volume}\"'
      args['mount'] = '${app} /q /v \"${volume}\" /l${where}'
      args['mountpw'] = '${app} /q /v \"${volume}\" /l${where} /p${pw}'
      args['dismount'] = '${app} /q /d${where}'
      args['dismountall'] = '${app} /q'
    else:
      args['automount'] = 'sudo ${app} -t -k "" --protect-hidden=no \"${volume}\"'
      args['mount'] = 'sudo ${app} -t -k "" --protect-hidden=no \"${volume}\" \"${where}\"'
      args['mountpw'] = 'sudo ${app} -t -k "" --protect-hidden=no -p \'${pw}\' \"${volume}\" \"${where}\"'
      args['dismount'] = 'sudo ${app} -t -d \"${where}\"'
      args['dismountall'] = 'sudo ${app} -t -d'
    return args

APP = 'truecrypt'

COMMANDS = get_commands()

def out(text):
    print(text)

def mount(volume, where, pw=None, validator=os.path.isdir, timeout=15):
    dictionary = { 'app': APP, 'volume': volume, 'where': where }
    out(utils.replacekeys('Mounting ${volume} at ${where} ...', dictionary))
    if pw is None:
      cmd = utils.replacekeys(COMMANDS['mount'], dictionary)
    else:
      dictionary.update({'pw': pw})
      cmd = utils.replacekeys(COMMANDS['mountpw'], dictionary)
    os.system(cmd)
    return wait(lambda: validator(where), timeout)

def automount(volume):
    dictionary = { 'app': APP, 'volume': volume }
    out(utils.replacekeys('Mounting ${volume} ...', dictionary))
    os.system(utils.replacekeys(COMMANDS['automount'], dictionary))

def dismount(where):
    dictionary = { 'app': APP, 'where': where }
    out(utils.replacekeys('Dismounting ${where} ...', dictionary))
    os.system(utils.replacekeys(COMMANDS['dismount'], dictionary))

def dismountall():
    dictionary = { 'app': APP }
    out('Dismounting all ...')
    os.system(utils.replacekeys(COMMANDS['dismountall'], dictionary))

def call(argv):
    parser = argparse.ArgumentParser(prog='truecrypt')
    subparsers = parser.add_subparsers(dest='cmd')
    for key, cmd in COMMANDS.items():
      subparser = subparsers.add_parser(key)
      for arg in re.findall(r"\$\{([A-Za-z0-9_]+)\}", cmd)[1:]:
        subparser.add_argument(arg)
    try:
      args = vars(parser.parse_args(argv))
    except SystemExit:
      return
    cmd = args.pop('cmd')
    args['app'] = APP
    os.system(utils.replacekeys(COMMANDS[cmd], args))

def wait(validator, time_out, time_step=1):
    if validator():
      return True
    try:
      out('Waiting for truecrypt ...')
      start = time.time()
      while (time.time() - start) < time_out:
        if validator():
          return True
        time.sleep(time_step)
    except KeyboardInterrupt:
      pass
    return False

class TruecryptException(Exception):
    pass

class TruecryptWrapper(object):
    def __init__(self, volume, where):
        if not mount(str(volume), str(where)):
          raise TruecryptException('Error mounting %s at %s.' % (volume, where))
        self.dismount = lambda: dismount(where)
