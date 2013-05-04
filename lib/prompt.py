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
