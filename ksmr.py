#!/usr/bin/env python
# Mikhail (myke) Koloodin
# 2025-05-27 2025-06-06 1.0.8

# --------------------------------------------------------------
# Стековая машина
# ksmc, интерпретатор байт-кода
# --------------------------------------------------------------

# --------------------------------------------------------------
# setup

version = '11'

# --------------------------------------------------------------
# imports

import sys
from loguru import logger
from pprint import pp, pprint
import random

# --------------------------------------------------------------
# in/out file names

if len(sys.argv) > 1:
    inout = sys.argv[1]
else:
    inout = 'prog01'

inname  = inout + '.smb'     # state machine program text
logname = inout + '.sml'     # state machine program log
outname = inout + '.smo'     # state machine program output

logger.remove()
logger.add(sys.stderr, level="WARNING")
logger.add(logname, level="DEBUG")

# print(f"Files: {inname=}, {outname=}, {logname=}")
logger.info(f"Files: {inname=}, {outname=}, {logname=}")

# --------------------------------------------------------------
# error level:
# 0: print nothing, 1: only important, 2: all
erlev = 2     

# size of numbers
UBYTEMOD = 256
UNUMMOD  = 65636
SBYTEMOD = 128
SNUMMOD  = 32768

HEADLEN = 4                  # length of code file header
MEMSIZE = 1024               # memory size

# opcodes, special
CODE_STOP    =  1
CODE_END     = 2
CODE_STRING  = 72

# character codes
CODE_SPACE   = 32

# limits

DSlen   =   256     # data stack
RSlen   =   256     # return stack
Memlen  =  1024     # memory
CFlen   = 65535     # code file 
CSlen   =   255     # control structures nesting

# --------------------------------------------------------------
# service functions

def check_ds(n: int) -> None:
    """check if DS has at least n elements and it not full"""
    
    assert len(ds) < DSlen, "DS overflow"
    assert len(ds) >= n, "DS underflow"

def check_rs(n: int) -> None:
    """check if RS has at least n elements and it not full"""
    
    assert len(rs) < RSlen, "RS overflow"
    assert len(rs) >= n, "RS underflow"

def check_memory(a: int) -> None:
    """check if address a is within memory size"""
    
    assert a >= 0, "Negatibe address"
    assert a < Memlen, "Out of memory size"

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

code2name = {}
for c, n, b, d in codes:
    code2name[c] = {'code': c, 'name': n, 'bytes': b, 'description': d}
# pprint(code2name)

# --------------------------------------------------------------
# read file with program, decompile byte code if needed

with open(inname, 'rb') as infile:
    # print(f"Reading code file from {inname} ...", end=" ")
    logger.info(f"Reading code file from {inname} ...", end=" ")
    cf = infile.read()
    # print("done.")
    logger.info("done.")

# print(cf)

# --------------------------------------------------------------
# check versions

if cf[:2] != 'SM'.encode('ascii'):
    print('The file read is not a binary from Stack Machine.')
    logger.error('The file read is not a binary from Stack Machine.')
    raise SystemExit

if cf[2:4] != version.encode('ascii'):
    print('The file read is from Stack Machine of wrong version.')
    logger.error('The file read is from Stack Machine of wrong version.')
    raise SystemExit

# --------------------------------------------------------------
# check checksum

csum = sum(cf[:-1]) % 256

assert csum == cf[-1], "Bad code file checksum."

# --------------------------------------------------------------
# prepare machine

# reset code file to rebase addresses
# cf = cf[4:]

# run time data structures

ds = []    # data stack
rs = []    # return stack

# flags as operation results 
flags = {'error': False, 
         'overflow': False}

# memory

memory = [0 for _ in range(MEMSIZE)]

# make output

# print(f"Writing log text to {logname}.\n")
logger.info(f"Writing log text to {logname}.")

# --------------------------------------------------------------
# run the code

with open(outname, 'wt') as outfile:

    # icode = -1
    icode = HEADLEN - 1

    try:

        while icode < len(cf):
            icode += 1
            
            code = cf[icode]
            
            # show opname
            opname = code2name[code]['name']
            oplen = code2name[code]['bytes']
            
            match oplen:
                case 1:
                    # print(f"{icode:04} {code:02} ({code:02X}) {opname:10}")
                    logger.info(f"{icode:04} {code:02} ({code:02X}) {opname:10}")
                    
                case 2:
                    # print(f"{icode:04} {code:02} {opname:10} {cf[icode+1]:4}")
                    logger.info(f"{icode:04} {code:02} {opname:10} {cf[icode+1]:4}")
                    # icode += 1
                    
                case 3:
                    x1 = cf[icode+1]
                    x2 = cf[icode+2]
                    s = x1 & 128
                    x1 &= 127
                    x = x1 * 256 + x2
                    x *= -1 if s else 1
                                    
                    # print(f"{icode:04} {code:02} {opname:10} {cf[icode+1]:4} {cf[icode+2]:4} ({x})")
                    logger.info(f"{icode:04} {code:02} {opname:10} {cf[icode+1]:4} {cf[icode+2]:4} ({x})")
                    # icode += 2
                    
                case _:
                    # print("???")
                    logger.error("???")
                    
            # print(f"{icode=}, {ds=}, {rs=}")
            logger.info(f"{icode=}, {ds=}, {rs=}")
                    
            match code:
                case 0: # 0   noop    1   no actions
                    pass
                    
                case 1: # 1   stop    1   stop program
                    pass
                    
                case 2: # 2   end 1   end of code
                    pass
                    
                case 12: # 12  dup 1   copy DS
                    check_ds(1)
                    ds.append(ds[-1])
                    
                case 13: # 13  drop    1    drop DS
                    check_ds(1)
                    ds.pop()
                    
                case 14: # 14  rot 1   move DS0@ to DS
                    check_ds(2)
                    n = ds.pop()
                    ds = ds[:-n] + ds[-n+1:] + [ds[-n]]
                    
                case 15: # 15  over    1    DS0@ to DS
                    check_ds(2)
                    n = ds.pop()
                    ds.append(ds[-n])
                    
                case 16: # 16  swap    1    swap DS1, DS0
                    check_ds(2)
                    ds[-2], ds[-1] = ds[-1], ds[-2]
                    
                case 10: # 10  dsrs    1    move DS0 to RS0
                    check_ds(1)
                    rs.append(ds.pop())
                    
                case 11: # 11  rsds    1    move RS0 to DS0
                    check_rs(1)
                    ds.append(rs.pop())
                    
                case 20: # 20  neg 1   change sign of DS0
                    check_ds(1)
                    ds[-1] *= -1
                    
                case 21: # 21  add 1   DS1 + DS0
                    check_ds(2)
                    flags['overflow'] = False
                    x = (ds.pop() + ds.pop()) % 65636
                    if -SNUMMOD < x or x > SNUMMOD:
                        flags['overflow'] = True
                    ds.append(x) 
                    
                case 22: # 22  sub 1   DS1 - DS0
                    check_ds(2)
                    flags['overflow'] = False
                    x = (- ds.pop() + ds.pop()) % 65636
                    if -SNUMMOD < x or x > SNUMMOD:
                        flags['overflow'] = True
                    ds.append(x)
                    
                case 23: # 23  mul 1   DS1 * DS0
                    check_ds(2)
                    flags['overflow'] = False
                    x = (ds.pop() * ds.pop()) % 65636
                    if -SNUMMOD < x or x > SNUMMOD:
                        flags['overflow'] = True
                    ds.append(x)
                    
                case 24: # 24  div 1   DS1 / DS0
                    check_ds(2)
                    flags['overflow'] = False
                    flags['error'] = False
                    x2 = ds.pop()
                    x1 = ds.pop()
                    if x2 == 0:
                        flags['error'] = True
                        ds.append(0)
                    else:
                        x = (x1 // x2) % 65636
                        if -SNUMMOD < x or x > SNUMMOD:
                            flags['overflow'] = True
                        ds.append(x)
                    
                case 25: # 25  mod 1   DS1 % DS0
                    check_ds(2)
                    flags['overflow'] = False
                    x2 = ds.pop()
                    x1 = ds.pop()
                    if x2 == 0:
                        flags['error'] = True
                        ds.append(0)
                    else:
                        x = (x1 % x2) % 65636
                        if -SNUMMOD < x or x > SNUMMOD:
                            flags['overflow'] = True
                        ds.append(x)
                    
                case 26: # 26  not 1   negate !DS0
                    check_ds(1)
                    ds.append( 1 if ds.pop() == 0 else 1)
                    
                case 27: # 27	random	1	random number to DS0
                    ds.append( random.randint(0, 65535) )
                    
                case 30: # 30  jump    3   goto label
                    x = cf[icode+1] * 256 + cf[icode+2]
                    icode = x - 1
                                    
                case 31: # 31  jeq 3   jump if DS0 == 0
                    check_ds(1)
                    if ds.pop() == 0:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 32: # 32  jne 3   jump if DS0 == 0
                    check_ds(1)
                    if ds.pop() != 0:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 33: # 33  jge 3   jump if DS0 == 0
                    check_ds(1)
                    if ds.pop() >= 0:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 34: # 34  jgt 3   jump if DS0 == 0
                    check_ds(1)
                    if ds.pop() > 0:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 35: # 35  jle 3   jump if DS0 == 0
                    check_ds(1)
                    if ds.pop() <= 0:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 36: # 36  jlt 3   jump if DS0 == 0
                    check_ds(1)
                    if ds.pop() < 0:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 37: # 37  jof 3   jump if DS0 == 0
                    if flags['overflow']:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 38: # 38  jef 3   jump if DS0 == 0
                    if flags['error']:
                        x = cf[icode+1] * 256 + cf[icode+2]
                        icode = x - 1
                    else:
                        icode += 2
                    
                case 40: # 40  calld    3   call subroutine directly by label
                    rs.append(icode+3)
                    x = cf[icode+1] * 256 + cf[icode+2]
                    icode = x - 1
                    # print(f"{ds=}, {rs=}")
                    
                case 41: # 41  calli  1   call subroutine indirectly from DS0
                    check_ds(1)
                    rs.append(icode+1)
                    icode = ds.pop() - 1
                    
                case 42: # 42  return  1   return from subroutine
                    check_rs(1)
                    icode = rs.pop() - 1
                    
                case 50: # 50  fetch   2   get value from memory
                    check_ds(1)
                    a = ds.pop()
                    check_memory(a)
                    ds.append( memory[a])
                    
                case 51: # 51  store   2   put value to memory
                    check_ds(2)
                    a = ds.pop()
                    v = ds.pop()
                    check_memory(a)
                    memory[a] = v
                    
                case 60: # 60  printnum    1   print number
                    check_ds(1)
                    x = ds.pop()
                    print(x, end=" ")
                    print(x, end=" ", file=outfile)
                    logger.success("output: " + str(x))
                    
                case 61: # 61  printchar   1   print character
                    check_ds(1)
                    x = chr(ds.pop())
                    print(x, end="")
                    print(x, end="", file=outfile)
                    logger.success(str(x))
                    
                case 62: # 62  println 1   print newline
                    print()
                    print(file=outfile)
                    logger.success("")
                    
                case 63: # 63  show    1   show system data
                    print(f"show: {ds=}, {rs=}, {icode=}, {flags=}")
                    print(f"show: {ds=}, {rs=}, {icode=}, {flags=}", file=outfile)
                    logger.success(f"show: {ds=}, {rs=}, {icode=}, {flags=}")
                    
                case 64: # 64  dump    1   dump system data
                    print(f"dump: {ds=}, {rs=}, {icode=}, {flags=}")
                    print(f"dump: {ds=}, {rs=}, {icode=}, {flags=}", file=outfile)
                    logger.success(f"dump: {ds=}, {rs=}, {icode=}, {flags=}")
                    print(f"{memory=}")
                    print(f"{memory=}", file=outfile)
                    logger.success(f"{memory=}")
                    
                case 65: # 65  wait   1    wait for enter key
                    input()
                    
                case 66: # 66  inputnum   1   wait for user input, get number
                    check_ds(0)
                    ds.append(int(input()))
                    
                case 67: # 67  inputchar   1   wait for user input, get character
                    check_ds(0)
                    ds.append(ord(input()[0]))
                    
                case 68: # 68  printstr    1   print string from DS0
                    check_ds(1)
                    x = ds.pop()
                    y = cf[x]
                    sout = ""
                    for ic in range(x+1, x+y+1):
                        ch = cf[ic]
                        sout += chr(ch)
                    print(sout, end="")
                    print(sout, end="", file=outfile)
                    logger.success(sout)
                    
                case 70: # 70  char    2   put char code to DS0
                    check_ds(0)
                    ds.append(cf[icode+1])
                    icode += 1
                    
                case 71: # 71  space   1   put space code to DS0
                    check_ds(0)
                    ds.append(CODE_SPACE)
                    
                case 72: # 72  string  1   put Hollerite string address to DS0
                    check_ds(0)
                    ds.append(icode+1)
                    icode += cf[icode+1] + 1

                case 73: # 10  byte    2   load number 0.255 to DS
                    check_ds(0)
                    ds.append(cf[icode+1])
                    icode += 1
                    
                case 74: # 11  number  3   load number -32768..32767
                    check_ds(0)
                    x1 = cf[icode+1]
                    x2 = cf[icode+2]
                    s = x1 & 128
                    x1 &= 127
                    x = x1 * 256 + x2
                    x *= -1 if s else 1
                    ds.append( x )
                    icode += 2

                case 75: # 75  addr   3   load address 0.65536 to DS
                    check_ds(0)
                    x1 = cf[icode+1]
                    x2 = cf[icode+2]
                    x = x1 * 256 + x2
                    ds.append( x )
                    icode += 2
                    
                case _:
                    print(f"\nValue error: illegal code {cf[icode]=} @ {icode=}, {ds=}, {rs=}")
                    logger.error(f"Value error: illegal code {cf[icode]=} @ {icode=}, {ds=}, {rs=}")
                    raise ValueError
            
            if code == CODE_STOP or code == CODE_END:   # stop, end
                break
        
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        logger.error(f"Assertion failed: {e}")
                
# print("\nJob done.\n")
print()
print()
logger.info("Job done.")

# --------------------------------------------------------------
# end of code
# --------------------------------------------------------------
