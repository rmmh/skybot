
import os
import re

from util import hook

@hook.command
def mem(bot):
    ".mem -- returns bot's current memory usage"

    if os.name=='posix':
        return posixmem()
    if os.name=='nt':
        return ntmem()

    return mem.__doc__


def posixmem():
    return _VmB('Size: ') + ' ' + _VmB('Resident:') + ' ' + _VmB('Stack:')

def ntmem():
    pid = os.getpid()
    total = 0
    
    cmd = "tasklist /FI \"PID eq {0}\" /FO CSV /NH".format(pid)
    e = re.compile("[,0-9]+ K")
    
    meml = re.findall(e,os.popen(cmd).read())
	
    if not mem1[0]:
        return 'This os does not have the tasklist command installed'
		
    for mem in meml:
        total += int(mem.rstrip(" K").replace(",",""))
		
    return 'Bot mem usage: ' + str(total) + ' K'

def _VmB(Key):
    '''Private'''
	
    _proc_status = '/proc/%d/status' % os.getpid()
	
    _scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
              'KB': 1024.0, 'MB': 1024.0*1024.0}
			  
    # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0
		
    # get Key line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(Key)
    v = v[i:].split(None, 3) 
    if len(v) < 3:
        return 0.0
		
    return float(v[1]) * _scale[v[2]]
