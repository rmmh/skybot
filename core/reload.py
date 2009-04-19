import glob
import collections

if 'plugin_mtimes' not in globals():
    mtimes = {}

def reload():
    init = False
    if not hasattr(bot, 'plugs'):
        bot.plugs = collections.defaultdict(lambda: [])
        init = True

    for filename in glob.glob("core/*.py"):
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            try:
                eval(compile(open(filename, 'U').read(), filename, 'exec'), 
                        globals())
                mtimes[filename] = mtime
            except Exception, e:
                print '    core error:', e
                continue

    for filename in glob.glob("plugins/*.py"):
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            try:
                code = compile(open(filename, 'U').read(), filename, 'exec')
                namespace = {}
                eval(code, namespace)
            except Exception, e:
                print '    error:', e
                continue

            # remove plugins already loaded from this filename
            for name, data in bot.plugs.iteritems():
                bot.plugs[name] = filter(lambda x: x[0][0] != filename, data)

            for obj in namespace.itervalues():
                if hasattr(obj, '_skybot_hook'): #check for magic
                    for type, data in obj._skybot_hook:
                        bot.plugs[type] += [data]

            mtimes[filename] = mtime

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

