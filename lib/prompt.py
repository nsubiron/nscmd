import platform

# Ask a yes/no question via input() and return their answer.
#   'question' is a string that is presented to the user.
#   'default' is the presumed answer if the user just hits <Enter>.
# It must be 'yes' (the default), 'no' or None (meaning an answer is required of
# the user). The 'answer' return value is one of 'yes' or 'no'.
def yes_no(question, default='yes'):
    valid = {'yes': True, 'y': True, 'no': False, 'n': False}
    prompts = {True: '[Y/n]', False: '[y/N]', None: '[y/n]'}
    try:
      if default is not None:
        default = valid[default.lower()]
      prompt = prompts[default]
    except KeyError:
      raise ValueError('Invalid default answer \'%s\'.' % default)
    while True:
      choice = raw_input('%s %s: ' % (question, prompt)).lower()
      if default is not None and choice == '':
        return default
      elif choice in valid:
        return valid[choice]
      else:
        print('Please answer \'%s\'.' % '\' or \''.join(valid.keys()))

if platform.system() == 'Windows':
  def color_string(string, *attributes):
      return string
else:
  def color_string(string, *attributes):
      """ If 'bold', it must be last attribute."""
      attrmap = {
        'bold': '1',
        'black': '0;30',
        'blue': '0;34',
        'brown': '0;33',
        'cyan': '0;36',
        'dark gray': '1;30',
        'green': '0;32',
        'light blue': '1;34',
        'light cyan': '1;36',
        'light gray': '0;37',
        'light green': '1;32',
        'light purple': '1;35',
        'light red': '1;31',
        'purple': '0;35',
        'red': '0;31',
        'white': '1;37',
        'yellow': '1;33'}
      attrstr = ';'.join(a for a in map(attrmap.get, attributes) if a is not None)
      return '\x1b[%sm%s\x1b[0m' % (attrstr, string)
