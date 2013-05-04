import os, inspect, fnmatch, platform

def which(program):
    exe_extensions = ['']
    if platform.system().lower() == 'windows':
      exe_extensions += ['.exe', '.bat']
    is_exe = lambda fpath: os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    get_exes = lambda name: [name + ext for ext in exe_extensions]
    fpath, fname = os.path.split(program)
    try:
      if fpath != '':
        return next(exe for exe in get_exes(program) if is_exe(exe))
      else:
        for path in os.environ['PATH'].split(os.pathsep):
          for exe_path in get_exes(os.path.join(path, program)):
            if is_exe(exe_path):
              return exe_path
    except StopIteration:
      pass
    return None

def find_files(root, includes=[], excludes=[]):
    if includes is None or len(includes) < 1:
      include = lambda f: True
    else:
      def include(f):
          for i in list(includes):
            if fnmatch.fnmatch(f, i):
              return True
    def validate(f):
        if include(f):
          for e in list(excludes):
            if fnmatch.fnmatch(f, e):
              return False
          return True
    lst = []
    for path, dirs, files in os.walk(root):
      lst += [os.path.join(path, f) for f in files if validate(f)]
    return lst
