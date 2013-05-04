import nsplugin, platform, sys, os, code

def throw():
    x = 1 / 0

class ThrowCommand(nsplugin.AppCommand):
    def run(self):
        throw()

    def help(self):
        throw()

    def complete_list(self):
        throw()

class SysinfoCommand(nsplugin.AppCommand):
    def run(self):
        print
        print('machine: ' + platform.machine())
        print('node: ' + platform.node())
        print('platform: ' + platform.platform())
        print('processor: ' + platform.processor())
        print
        print('system: ' + platform.system())
        print('release: ' + platform.release())
        print('version: ' + platform.version())
        print
        print('python_build_no: ' + platform.python_build()[0])
        print('python_build_date: ' + platform.python_build()[1])
        print('python_compiler: ' + platform.python_compiler())
        print('python_branch: ' + platform.python_branch())
        print('python_implementation: ' + platform.python_implementation())
        print('python_revision: ' + platform.python_revision())
        print('python_version: ' + platform.python_version())
        print
        print('sys.path:')
        for path in sys.path:
          print('  ' + path)
        print('PATH:')
        for path in os.environ['PATH'].split(os.pathsep):
          print('  ' + path)
        print

    def help(self):
        print('Print system information.')

class PythoncmdCommand(nsplugin.AppCommand):
    def run(self):
        python_console = code.InteractiveConsole()
        python_console.interact()

    def help(self):
        print('Launch a python interactive console inside this application.')
