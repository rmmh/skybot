'''brainfuck interpreter adapted from (public domain) code at
http://brainfuck.sourceforge.net/brain.py'''

import re
import random

BUFFER_SIZE = 5000

#command
def bf(bot, inp, input=None, max_steps=1000000, no_input=0):
    """Runs a Brainfuck program given as a string.
    
    The string must contain nothing but "<>[]+-.,", i.e.
    be already filtered.
        
    If 'input' is None, stdin is used. 'input' can be
    a string or a tuple; tuples are only used if
    extended_interpretation is non-zero, and should
    be more or less obvious in that case.
    
    if max_steps is < 0, there is no restriction."""
    program = re.sub('[^][<>+-.,]', '', inp.inp)
    
    # create a dict of brackets pairs, for speed later on
    parens={}
    open_parens=[]
    for pos in range(len(program)):
        if program[pos] == '[':
            open_parens.append(pos)
        elif program[pos] == ']':
            if len(open_parens) > 0:
                parens[pos] = open_parens[-1]
                parens[open_parens[-1]] = pos
                open_parens.pop()
            else:
                return 'unbalanced brackets'
#    if len(open_parens) != 0:
#        return 'unbalanced brackets'
    # now we can start interpreting
    pc = 0        # program counter
    mp = 0        # memory pointer
    steps = 0 
    memory = [0] * BUFFER_SIZE  #initial memory area
    rightmost = 0
    if input != None:
        if type(input) == type(()):
            # we'll only be using input[0] right now
            inputs, input = input, input[0]
        input_pointer = 0
    
    output = ""   #we'll save the output here
    
    if no_input:
        eof_reached = 1
    else:
        eof_reached = 0
        
    # the main program loop:
    while pc < len(program):
        c = program[pc]
        if   c == '+':
            memory[mp] = memory[mp] + 1 % 256
        elif c == '-':
            memory[mp] = memory[mp] - 1 % 256
        elif c == '>':
            mp = mp + 1
            if mp > rightmost:
                rightmost = mp
                if mp >= len(memory):
                    memory = memory + [0]*BUFFER_SIZE # no restriction on memory growth!
        elif c == '<':
            mp = mp - 1 % len(memory)
        elif c == '.':
            output += chr(memory[mp])
            if len(output) > 500:
                break
                
        elif program[pc] == ',':
            if eof_reached:
                raise Exception, "Program tries reading past EOF"
            if input == None:
                #char = sys.stdin.read(1)
                char = chr(random.randint(1,255))
                if char == '': # EOF
                    memory[mp] = 0
                    eof_reached = 1
                else:
                    memory[mp] = ord(char)
            else:
                if input_pointer == len(input): # EOF
                    memory[mp] = 0
                    eof_reached = 1
                else:
                    memory[mp] = ord(input[input_pointer])
                    input_pointer = input_pointer + 1
                
        elif program[pc] == '[':
            if memory[mp] == 0:
                pc = parens[pc]
                
        elif program[pc] == ']':
            if memory[mp] != 0:
                pc = parens[pc]
                
        pc += 1
        steps += 1
        if max_steps >= 0 and steps > max_steps:
            output += "Maximum number of steps exceeded"
            break
        
        # end of while loop
    
    return unicode(re.sub('[\r\n\x00]', '/', output), 'iso-8859-1')[:400]
