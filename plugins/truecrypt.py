import nsplugin
from lib import truecrypt

class TruecryptCommand(nsplugin.AppCommand):
    def run(self, argv):
        truecrypt.call(argv[1:])

    def help(self):
        truecrypt.call(['-h'])

    def complete_list(self):
        return truecrypt.COMMANDS.keys()
