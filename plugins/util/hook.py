import inspect
import thread
import traceback
import Queue

def _isfunc(x):
    if type(x) == type(_isfunc):
        return True
    return False


def _hook_add(func, add, name=''):
    if not hasattr(func, '_skybot_hook'):
        func._skybot_hook = []
    func._skybot_hook.append(add)
    if not hasattr(func, '_skybot_args'):
        argspec = inspect.getargspec(func)
        if name:
            n_args = len(argspec.args)
            if argspec.defaults:
                n_args -= len(argspec.defaults)
            if argspec.keywords:
                n_args -= 1
            if argspec.varargs:
                n_args -= 1
            if n_args != 1:
                err = '%ss must take 1 non-keyword argument (%s)' % (name, 
                            func.__name__)
                raise ValueError(err)

        args = []
        if argspec.defaults:
            end = bool(argspec.keywords) + bool(argspec.varargs)
            args.extend(argspec.args[-len(argspec.defaults):
                        end if end else None])
        if argspec.keywords:
            args.append(0) # means kwargs present
        func._skybot_args = args

def _make_sig(f):
    return f.func_code.co_filename, f.func_name, f.func_code.co_firstlineno


def sieve(func):
    if func.func_code.co_argcount != 4:
        raise ValueError(
                'sieves must take 4 arguments: (bot, input, func, args)')
    _hook_add(func, ['sieve', (_make_sig(func), func)])
    return func


def command(func=None, hook=None, **kwargs):
    args = {}

    def command_wrapper(func):
        args.setdefault('name', func.func_name)
        args.setdefault('hook', args['name'] + r'(?:\s+|$)(.*)')
        _hook_add(func, ['command', (_make_sig(func), func, args)], 'command')
        return func

    if hook is not None or kwargs or not _isfunc(func):
        if func is not None:
            args['name'] = func
        if hook is not None:
            args['hook'] = hook
        args.update(kwargs)
        return command_wrapper
    else:
        return command_wrapper(func)


def event(arg=None, **kwargs):
    args = kwargs

    def event_wrapper(func):
        args['name'] = func.func_name
        args['prefix'] = False
        args.setdefault('events', '*')
        _hook_add(func, ['event', (_make_sig(func), func, args)], 'event')
        return func

    if _isfunc(arg):
        return event_wrapper(arg, kwargs)
    else:
        if arg is not None:
            args['events'] = arg.split()
        return event_wrapper


def tee(func, **kwargs):
    "passes _all_ input lines to function, in order (skips sieves)"

    if func.func_code.co_argcount != 2:
        raise ValueError('tees must take 2 arguments: (bot, input)')

    _hook_add(func, ['tee', (_make_sig(func), func, kwargs)])
    func._iqueue = Queue.Queue()

    def trampoline(func):
        input = None
        while True:
            input = func._iqueue.get()
            if input == StopIteration:
                return
            try:
                func(*input)
            except Exception:
                traceback.print_exc(Exception)

    thread.start_new_thread(trampoline, (func,))

    return func
