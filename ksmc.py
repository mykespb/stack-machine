#!/usr/bin/env python
# Mikhail (myke) Kolodin
# 2025-05-27 2025-06-06 1.0.8

# --------------------------------------------------------------
# Стековая машина - Stack machine
# ksmc, bytes codes compiler, компилятор в байт-код
# --------------------------------------------------------------

# --------------------------------------------------------------
# setup

version = '11'

# --------------------------------------------------------------
# imports

import sys
from loguru import logger
from pprint import pp, pprint
from collections import defaultdict

# --------------------------------------------------------------
# in/out file names

print(f"{sys.argv=}")

if len(sys.argv) > 1:
    inout = sys.argv[1]
else:
    inout = 'prog01'

if len(inout) > 4 and inout[-4] == '.':
    inout = inout[:-4]

inname  = inout + '.smt'     # state machine program text
outname = inout + '.smb'     # state machine program binary
logname = inout + '.sml'     # state machine log file

logger.remove()
logger.add(logname)

print(f"Files: {inout=}, {inname=}, {outname=}, {logname=}")
logger.info(f"Files: {inout=}, {inname=}, {outname=}, {logname=}")

HEADLEN = 4                  # length of code file header

# opcodes, special
CODE_STOP    = 1
CODE_END     = 2
CODE_CHAR    = 70
CODE_STRING  = 72
CODE_JEQ     = 31
CODE_JNE     = 32
CODE_JUMP    = 30
CODE_DSRS    = 10
CODE_RSDS    = 11
CODE_DUP     = 12
CODE_SUB     = 22
CODE_BYTE    = 73
CODE_NUMBER  = 74

# limits

DSlen   =   256     # data stack
RSlen   =   256     # return stack
Memlen  =  1024     # memory
CFlen   = 65535     # code file 
CSlen   =   255     # control structures nesting

# --------------------------------------------------------------
# get data about machine codes

codes = []

## normal version, with tabs, checked + corrected
codesname = 'opcodes.tsv'
with open(codesname, 'rt') as codesfile:
    line = codesfile.readline()
    for line in codesfile.readlines():
        c, n, b, d = line.strip().split('\t', maxsplit=3)
        c = int(c)
        b = int(b)
        codes.append((c, n, b, d))
# pprint(codes)

name2code = {}
for c, n, b, d in codes:
    name2code[n] = {'code': c, 'name': n, 'bytes': b, 'description': d}
# pprint(name2code)

# pseudocommands (macros etc) (TBD)
pseudos = "label if then else do loop begin while repeat macro name const version model" . split()

# code memory
cf = bytearray()

# labels defines: name -> addr
labset = {}
# labels references: addr -> name
labref = {}

# make header
cf.extend(('SM' + version).encode('ascii'))

# make contents: program code

# compiler state
state = "normal"
# others: "getlabel", "setlabel", "getbyte", "getnumber", "getstring", "getchar", "macrodef"

class EOP (Exception): pass

# control structures
ctrlstr = []
ctrllev = []
ctrlnum = 0

# macros
macros = defaultdict(str)

# consts
consts = {}

# error state on command loop
isError = True

# --------------------------------------------------------------
# check functions

def check_cf():
    """check code file length"""
    
    assert len(cf) <= CFlen

# --------------------------------------------------------------
# read file with program, write byte code

# process files
with open(inname, 'rt') as inf:
    
    try:
    
        # main loop
        for iline, line in enumerate(inf, 1):
            
            isError = False
            check_cf()
            
            line = line.strip()
            
            print(iline, line)
            logger.info(f"{iline=}: {line.strip()}")
            
            # check for macro call
            if line.startswith('_'):
                macroname, *params = line.split()
                line = macros[macroname]
                
                for i in range(len(params)):
                    str_from = "$"+str(i)
                    str_to = params[i]
                    line = line.replace(str_from, str_to)
                    print(f"replace({str_from=}, {str_to=})")
                    
                print(f"{line=}")
                logger.info(f"{line=}")
            
            # check for macro call
            elif line.startswith('macro'):
                macroname = line.split()[1]
                if macroname in macros:
                    print(f"Error: duplicate macro name: {macroname}")
                    logger.error(f"Error: duplicate macro name: {macroname}")
                    raise EOP
                # ok
                state = 'macrodef'
                continue
                
            elif state == 'macrodef':
                if len(line):
                    macros[macroname] += " " + line
                else:
                    state = 'normal'
                    print(f"macro def '{macroname}': {macros[macroname]}")
                    logger.info(f"macro def '{macroname}': {macros[macroname]}")
                continue
            # end of macro checks
            
            for iword, word in enumerate(line.split(), 1):
                
                print("\t", iword, word, end=" ")
                logger.info(f"{iword=}, {word=}")
                
                # comments
                if word == '#' or word == ';':
                    print("comment")
                    logger.info("comment")
                    break
                
                # commands
                print(f"{state=}, {word=}, {len(cf)=}")
                logger.info(f"{state=}, {word=}, {len(cf)=}")

                # chars
                if word.startswith("'") and word.endswith("'"):
                    cf.append(CODE_CHAR)
                    cf.append( ord(word.strip("'")) )
                    continue
                
                # strings
                if word.startswith('"') and word.endswith('"'):
                    cf.append(CODE_STRING)
                    word = word.strip('\"')
                    cf.append( len(word) )
                    for ch in word:
                        cf.append( ord(ch) )
                    continue

                # general processing
                
                match state:
                    
                    case 'normal':

                        if word in consts:
                            x = consts[word]
                            if 0 <= x <= 255:
                                cf.append(CODE_BYTE)
                                cf.append( x )
                                print(f"Added byte {x} as const {const_name} for word {word}")
                                logger.info(f"Added byte {x} as const {const_name} for word {word}")
                            else:
                                s = 0 if x >= 0 else 128
                                x = abs(x)
                                x1 = x // 256
                                x2 = x % 256
                                cf.append(CODE_NUMBER)
                                cf.append( s | x1 )
                                cf.append( x2 )
                                print(f"Added number {x} as const {const_name} for word {word}")
                                logger.info(f"Added number {x} as const {const_name} for word {word}")
                            state = 'normal'
                            continue       

                        if word in pseudos:
                            print(f": pseudo '{word}' detected...")
                            logger.info(f": pseudo '{word}' detected...")

                            match word:
                                
                                case 'label':
                                    state = 'deflabel'
                                    # print('state = deflabel!')

                                case 'const':
                                    state = 'defconst1'
                                    # print('state = defconst!')
                                    
                                case 'if':
                                    ctrlnum += 1
                                    ctrllev.append(ctrlnum)
                                    ctrlstr.append('if')
                                    cf.append(CODE_JEQ)
                                    labref[len(cf)] = f'if_{ctrllev[-1]}'
                                    cf.append(0)
                                    cf.append(0)
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    
                                case 'else':
                                    if ctrlstr[-1] != 'if':
                                        logger.error(f"else outside if")
                                        raise EOP
                                    ctrlstr[-1] = 'ifelse'
                                    cf.append(CODE_JUMP)
                                    labref[len(cf)] = f'else_{ctrllev[-1]}'
                                    cf.append(0)
                                    cf.append(0)
                                    labset[f'if_{ctrllev[-1]}'] = len(cf)
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    
                                case 'then':
                                    if ctrlstr[-1] == 'if':
                                        labset[f'if_{ctrllev[-1]}'] = len(cf)
                                    elif ctrlstr[-1] == 'ifelse':
                                        labset[f'else_{ctrllev[-1]}'] = len(cf)
                                    else:
                                        logger.error(f"then outside if")
                                        raise EOP
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    ctrlstr.pop()
                                    ctrllev.pop()
                                
                                case 'begin':
                                    ctrlnum += 1
                                    ctrllev.append(ctrlnum)
                                    ctrlstr.append('begin')
                                    labset[f'begin_{ctrllev[-1]}'] = len(cf)
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    
                                case 'while':
                                    if ctrlstr[-1] != 'begin':
                                        logger.error(f"while outside begin")
                                        raise EOP
                                    cf.append(CODE_JEQ)
                                    labref[len(cf)] = f'repeat_{ctrllev[-1]}'
                                    cf.append(0)
                                    cf.append(0)
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    
                                case 'repeat':
                                    if ctrlstr[-1] != 'begin':
                                        logger.error(f"repeat outside begin")
                                        raise EOP
                                    cf.append(CODE_JUMP)
                                    labref[len(cf)] = f'begin_{ctrllev[-1]}'
                                    cf.append(0)
                                    cf.append(0)
                                    labset[f'repeat_{ctrllev[-1]}'] = len(cf)
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    ctrlstr.pop()
                                    ctrllev.pop()
                                
                                case 'do':
                                    ctrlnum += 1
                                    ctrlstr.append('do')
                                    ctrllev.append(ctrlnum)
                                    cf.append(CODE_DSRS)
                                    labset[f'do_{ctrllev[-1]}'] = len(cf)
                                    cf.append(CODE_RSDS)
                                    cf.append(CODE_DUP)
                                    cf.append(CODE_DSRS)
                                    cf.append(CODE_JEQ)
                                    labref[len(cf)] = f'loop_{ctrllev[-1]}'
                                    cf.append(0)
                                    cf.append(0)
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    
                                case 'loop':
                                    if ctrlstr[-1] != 'do':
                                        logger.error(f"loop outside do")
                                        raise EOP
                                    cf.append(CODE_RSDS)
                                    cf.append(CODE_BYTE)
                                    cf.append(1)
                                    cf.append(CODE_SUB)
                                    cf.append(CODE_DSRS)
                                    cf.append(CODE_JUMP)
                                    labref[len(cf)] = f'do_{ctrllev[-1]}'
                                    cf.append(0)
                                    cf.append(0)
                                    labset[f'loop_{ctrllev[-1]}'] = len(cf)
                                    logger.debug(f"{ctrlnum=}, {ctrlstr[-1]=}, {ctrllev=}")
                                    ctrlstr.pop()
                                    ctrllev.pop()
                                
                                case _:
                                    print(f"Cannot find exec for pseudo '{word}'")
                                    logger.error(f"Cannot find exec for pseudo '{word=}'")
                                    state = 'normal'                                    

                        elif word in name2code:
                            addcode = name2code[word]['code']
                            cf.append(addcode) 
                            print(f"\t({addcode=})")
                            logger.info(f"({addcode=})")
                            
                            match word:
                                
                                case 'byte':
                                    state = 'getbyte'
                                
                                case 'number':
                                    state = 'getnumber'
                                
                                case 'char':
                                    state = 'getchar'
                                
                                case 'string':
                                    state = 'getstring'
                                
                                case 'jump' | 'jeq' | 'jne' | 'jge' | 'jgt' | 'jle' | 'jlt' | 'jof' | 'jef' | 'calld' | 'addr' :
                                    state = 'reflabel'
                                
                                case 'end':
                                    print("\nEnd of program...", end=" ")
                                    logger.info("End of program...")
                                    raise EOP

                        else:
                            print(f"{state=}, {word=}, {len(cf)=}")
                            n = int(word)
                            
                            if 0 <= n <= 255:
                                cf.append(73)
                                cf.append(n)
                                
                            elif -32768 <= n <= 32767:
                                s = 0 if n >= 0 else 128
                                n = abs(n)
                                x1 = n // 256
                                x2 = n % 256
                                cf.append(74)
                                cf.append( s | x1 )
                                cf.append( x2 )                                
                                
                            else:
                                print("Value Error")
                                logger.error("Value Error")
                                raise ValueError

                            print()                            
                            state = 'normal'

                    case 'defconst1':
                        
                        if (word in name2code or 
                            word in pseudos or 
                            word in macros):
                            print(f"Errorr: const '{word}' is duplicate.")
                            logger.error(f"Errorr: const '{word}' is duplicate.")
                        else:
                            state = 'defconst2'
                            const_name = word

                    case 'defconst2':
                        
                        try:
                            x = int(word)
                            consts[const_name] = x
                        except:
                            print(f"Error: bad number for constant: {word}")
                        print(f"{consts=}")
                        logger.info(f"{consts=}")
                            
                        state = 'normal'

                    case 'deflabel':                    
                        
                        if word in labset:
                            print(f"Duplicate label: {word}")
                            logger.error(f"Duplicate label: {word}")
                            raise EOP
                        
                        # ok
                        print(f"deflabel: {len(cf)=}, {word=}")
                        logger.info(f"deflabel: {len(cf)=}, {word=}")
                        labset[word] = len(cf)
                        # labset[word] = len(cf) - HEADLEN
                        # logger.debug(labels)
                        print()
                        
                        state = 'normal'

                    case 'reflabel':                    
                        
                        print(f"reflabel: {len(cf)=}, {word=}")
                        logger.info(f"reflabel: {len(cf)=}, {word=}")
                        labref[len(cf)] = word
                        # labref[len(cf) - HEADLEN] = word
                        cf.append(0)
                        cf.append(0)
                        # print()
                        # logger.debug(labels)
                        
                        state = 'normal'

                    case 'getbyte':

                        cf.append(int(word) % 256)
                        
                        state = 'normal'

                    case 'getnumber':

                        s = 0 if word >= 0 else 128
                        word = abs(word)
                        x1 = word // 256
                        x2 = word % 256
                        cf.append( s | x1 )
                        cf.append( x2 )
                        
                        state = 'normal'

                    case 'getchar':

                        cf.append( ord(word) )
                        
                        state = 'normal'

                    case 'getstring':

                        los = len(word)
                        if los >= 256:
                            logger.error("String too long: " + int(los))
                            raise ValueError
                        cf.append( los )
                        for c in word:
                            cf.append( ord(c) )
                        
                        state = 'normal'

                    case _:

                        logger.error("Strange word: " + word)
                        
                        state = 'normal'
                        
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        logger.error(f"Assertion failed: {e}")
        isError = True
        
    except EOP:
        print(f"File {inname} processed.")

if cf[-1] != CODE_END:
    cf.append(CODE_END)
    print("Opcode for END added.")
    logger.info("Opcode for END added.")

print("done.")

# file processing done.

# show and process labels:

if labset:
    print("\nLabels:")
    print(f"{labset=}")
    print(f"{labref=}")

    logger.info("Labels:")
    logger.info(f"{labset=}")
    logger.info(f"{labref=}")

    for k, v in labref.items():
        x = labset[v]
        x1 = x // 256
        x2 = x % 256
        cf[k] = x1
        cf[k+1] = x2
        # cf[k + HEADLEN] = x1
        # cf[k+1 + HEADLEN] = x2
    
else:
    print("\nNo labels defined.")
    logger.info("No labels defined.")

# show macros:

if macros:
    lom = ", " .join (list(macros.keys()))
    print(f"\nMacros defined: {lom}")
    logger.info(f"Macros defined: {lom}")
else:
    print("\nNo macros defined.")
    logger.info("No macros defined.")

# make checksum

cf.append( sum(cf) % 256 )

# save cf in binary file

with open(outname, 'wb') as outfile:
    outfile.write(cf)

# Job done:

print("\nJob done %s.\n" % ("with errors" if isError else "without errors"))
logger.info("Job done %s.\n" % ("with errors" if isError else "without errors"))

# --------------------------------------------------------------
# end of code
# --------------------------------------------------------------
