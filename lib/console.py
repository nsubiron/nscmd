import cmd, os, fnmatch, prompt

class Console(cmd.Cmd, object):
    def emptyline(self):
        pass

    def default(self, line):
        print('Unknown command \'%s\'!' % line)

    def can_exit(self):
        return True

    def onecmd(self, line):
        r = super (Console, self).onecmd(line)
        if r and (self.can_exit() or prompt.yes_no('exit anyway?', 'no')):
          return True
        return False

    def do_exit(self, s):
        """Exit the console."""
        return True

    def do_EOF(self, s):
        """Exit the console."""
        print('exit')
        return self.do_exit(s)

    def help_help(self):
        print('usage: help [topic]')

def complete_cd(text, line, start_index, end_index, onlyDirs):
    path = ''
    if end_index == len(line):
      # @todo Use find to split just the 'cd ' term. This doesn't support
      # spaces in the path.
      split = line.split()
      if len(split) > 1:
        path = os.path.join(os.getcwd(), split[-1])
        path = path.replace(text, '')
    if not os.path.isdir(path):
      path = os.getcwd()
    complete_list = []
    for d in os.listdir(path):
      if os.path.isdir(os.path.join(path, d)):
        complete_list.append(d + '/')
      elif not onlyDirs:
        complete_list.append(d)
    if text:
      return [
        field for field in complete_list
        if field.startswith(text)
      ]
    else:
      return complete_list

class DirectoryExplorer(Console):
    def __init__(self, prefix=None):
        Console.__init__(self)
        user = os.path.expanduser('~')
        getcwd = lambda: os.getcwd().replace(user, '~')
        if prefix is not None:
          self.get_prompt = lambda: '%s:%s>' % (prefix, getcwd())
        else:
          self.get_prompt = lambda: '%s>' % getcwd()
        self.oldpwd = ''
        self.update_prompt()

    def update_prompt(self):
        self.prompt = self.get_prompt()

    def postcmd(self, stop, line):
        self.update_prompt()
        return stop

    def do_cd(self, line):
        """usage: cd [dir]"""
        if not line:
          line = os.path.expanduser('~')
        elif line == '-':
          line = self.oldpwd
          print('cd %s' % line)
        if os.path.isdir(str(line)):
          self.oldpwd = os.getcwd()
          os.chdir(str(line))
        else:
          print('Error! directory not found.')

    def complete_cd(self, text, line, start_index, end_index):
        return complete_cd(text, line, start_index, end_index, True)

    def completedefault(self, text, line, start_index, end_index):
        return complete_cd(text, line, start_index, end_index, False)

class Shell(DirectoryExplorer):
    def __init__(self, prefix):
        DirectoryExplorer.__init__(self, prefix)
        self.parse_aliases()

    def parse_aliases(self):
        self.aliases = {}
        for bash_file in ['.bashrc', '.bash_aliases']:
          bash_file = os.path.join(os.path.expanduser('~'), bash_file)
          try:
            for line in open(bash_file, 'r'):
              line = line.strip()
              if fnmatch.fnmatch(line, 'alias *'):
                self.do_alias(line.partition(' ')[2])
          except IOError:
            pass

    def do_alias(self, line):
        """usage:
  alias                      to print current aliases.
  alias <alias>=\'<command>\'  to add an alias.

note: This will be only valid during current session, if you want to store it
permanently add it to \'~/.bash_aliases\'.
"""
        if not line or line.isspace():
          for alias in self.aliases.keys():
            print('alias %s=\'%s\'' % (alias, self.aliases[alias]))
        else:
          alias, sep, command = line.partition('=')
          command = command.strip()[1:-1]
          self.aliases[alias] = command

    def do_shell(self, line):
        """Execute shell commands. Note: By default, unrecognized commands are
passed to shell."""
        cmd, sep, args = line.partition(' ')
        if cmd in self.aliases.keys():
          alias = self.aliases[cmd]
          if alias not in line:
            return self.do_shell(alias + sep + args)
        os.system(line)

    # If not recognized, try to run as shell.
    def default(self, line):
        self.do_shell(line)
