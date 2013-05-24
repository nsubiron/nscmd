import fnmatch, os, platform, re

DEFAULT_PATHEXT = ['']
if platform.system().lower() == 'windows':
  DEFAULT_PATHEXT += ['.com', '.exe', '.bat', '.cmd']

def which(name, flags=os.X_OK):
    """Return the full path to the first executable found in the environmental
    variable PATH matching the given name."""
    envpath = os.environ.get('PATH', None)
    if envpath is None:
      return None
    exts = set(os.environ.get('PATHEXT', '').split(os.pathsep) + DEFAULT_PATHEXT)
    for path in envpath.split(os.pathsep):
      pname = os.path.join(path, name)
      if os.access(pname, flags):
        return pname
      for ext in exts:
        pnameext = pname + ext
        if os.access(pnameext, flags):
          return pnameext
    return None

def regex_callable(patterns):
    """Return a callable object that returns True if matches any regular
    expression in patterns"""
    if patterns is None:
      return lambda x: False
    if isinstance(patterns, str):
      patterns = [patterns]
    r = re.compile(r'|'.join(fnmatch.translate(p) for p in patterns))
    return lambda x: r.match(x) is not None

def walk(root, file_includes=['*'], file_excludes=None, dir_excludes=['.git', '.svn']):
    """Convenient wrap around os.walk. Patterns are checked on base names, not
    on full path names."""
    fincl = regex_callable(file_includes)
    fexcl = regex_callable(file_excludes)
    dexcl = regex_callable(dir_excludes)
    for path, dirs, files in os.walk(os.path.abspath(root)):
      dirs[:] = [d for d in dirs if not dexcl(d)]
      files[:] = [f for f in files if fincl(f) and not fexcl(f)]
      yield path, dirs, files

def fwalk(*args, **kwargs):
    """Walk over the full path of the files matching the arguments given. See
    utils.walk."""
    for path, _, files in walk(*args, **kwargs):
      for f in files:
        yield os.path.join(path, f)

def replacekeys(obj, dictionary):
    """Replace any ${key} occurrence in obj by its value in dictionary."""
    if obj is None:
      return None
    elif isinstance(obj, str) or isinstance(obj, unicode):
      for key, value in dictionary.items():
        obj = obj.replace('${%s}' % key, value)
      return obj
    elif isinstance(obj, dict):
      return dict((k, replacekeys(i, dictionary)) for k, i in obj.items())
    elif any(isinstance(obj, x) for x in [tuple, list, set]):
      return map(lambda i: replacekeys(i, dictionary), obj)
    elif any(isinstance(obj, x) for x in [bool, int, float, long, complex]):
      return obj
    else:
      raise Exception('Type object \'%s\' not implemented.' % type(obj))
