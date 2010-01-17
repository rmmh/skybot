import Queue
import thread
import traceback

def _isfunc(x):
    if type(x) == type(_isfunc):
        return True
    return False


def _hook_add(func, add):
    if not hasattr(func, '_skybot_hook'):
        func._skybot_hook = []
    func._skybot_hook.append(add)


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
        if func.func_code.co_argcount not in (1, 2):
            raise ValueError(
                'commands must take 1 or 2 arguments: (inp) or (bot, input)')
        args.setdefault('name', func.func_name)
        args.setdefault('hook', args['name'] + r'(?:\s+|$)(.*)')
        _hook_add(func, ['command', (_make_sig(func), func, args)])
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
        if func.func_code.co_argcount != 2:
            raise ValueError('events must take 2 arguments: (bot, input)')
        args['name'] = func.func_name
        args['prefix'] = False
        args.setdefault('events', '*')
        _hook_add(func, ['event', (_make_sig(func), func, args)])
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
