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
        """Print system information."""
        print
        platforminfo = ['machine', 'node', 'platform', 'processor', 'system',
                        'release', 'version', 'python_build', 'python_compiler',
                        'python_implementation', 'python_version']
        for i in platforminfo:
          if hasattr(platform, i):
            print('%s: %s' % (i, getattr(platform, i)()))
        print
        print('sys.path:\n  ' + '\n  '.join(sys.path))
        print
        print('PATH:\n  ' + '\n  '.join(os.environ['PATH'].split(os.pathsep)))
        print

class PythoncmdCommand(nsplugin.AppCommand):
    def run(self):
        """Launch a python interactive console inside this application."""
        python_console = code.InteractiveConsole()
        python_console.interact()
