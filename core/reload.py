import glob
import collections
import traceback

if 'mtimes' not in globals():
    mtimes = {}

if 'lastfiles' not in globals():
    lastfiles = set()

def reload():
    init = False
    if not hasattr(bot, 'plugs'):
        bot.plugs = collections.defaultdict(lambda: [])
        init = True

    for filename in glob.glob("core/*.py"):
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            mtimes[filename] = mtime
            try:
                eval(compile(open(filename, 'U').read(), filename, 'exec'), 
                        globals())
            except Exception:
                traceback.print_exc(Exception)
                continue

            if filename == 'core/reload.py':
                reload()
                return

    fileset = set(glob.glob("plugins/*py"))
    for name, data in bot.plugs.iteritems(): # remove deleted/moved plugins
        bot.plugs[name] = filter(lambda x: x[0][0] in fileset, data)

    for filename in fileset:
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            mtimes[filename] = mtime
            try:
                code = compile(open(filename, 'U').read(), filename, 'exec')
                namespace = {}
                eval(code, namespace)
            except Exception:
                traceback.print_exc(Exception)
                continue

            # remove plugins already loaded from this filename
            for name, data in bot.plugs.iteritems():
                bot.plugs[name] = filter(lambda x: x[0][0] != filename, data)

            for obj in namespace.itervalues():
                if hasattr(obj, '_skybot_hook'): #check for magic
                    for type, data in obj._skybot_hook:
                        bot.plugs[type] += [data]

    if init:
        print '  plugin listing:'
        for type, plugs in sorted(bot.plugs.iteritems()):
            print '    %s:' % type
            for plug in plugs:
                out = '      %s:%s:%s' % (plug[0])
                print out,
                if len(plug) == 3 and 'hook' in plug[2]:
                    print '%s%s' % (' ' * (40 - len(out)), plug[2]['hook'])
                else:
                    print
        print
