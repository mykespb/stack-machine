#!/usr/bin/env python
# Mikhail (myke) Koloodin
# 2025-05-27 2025-06-06 1.0.8

# --------------------------------------------------------------
# Стековая машина - Stack machine
# ksmc, bytes codes compiler, декомпилятор из байт-кода
# --------------------------------------------------------------

# --------------------------------------------------------------
# setup

version = '11'

# --------------------------------------------------------------
# imports

import sys
from loguru import logger
from pprint import pp, pprint

# --------------------------------------------------------------
# in/out file names

if len(sys.argv) > 1:
    inout = sys.argv[1]
else:
    inout = 'prog01'

inname  = inout + '.smb'     # state machine program binary
decname = inout + '.smd'     # state machine program decomplied
logname = inout + '.sml'     # state machine log file

logger.add(logname)

print(f"Files: {inname=}, {decname=}, {logname=}")
logger.info(f"Files: {inname=}, {decname=}, {logname=}")

HEADLEN = 4                  # length of code file header

# opcodes, special
CODE_STOP    =  1
CODE_END     = 2
CODE_STRING  = 72

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
# read file with program, decompile byte code

with open(inname, 'rb') as infile:
    print(f"Reading code file from {inname} ...", end=" ")
    cf = infile.read()
    print("done.")
    
# print(cf)

# --------------------------------------------------------------
# check versions

if cf[:2] != 'SM'.encode('ascii'):
    print('The file read is not a binary from Stack Machine.')
    raise SystemExit

if cf[2:4] != version.encode('ascii'):
    print('The file read is from Stack Machine of wrong version.')
    raise SystemExit

# --------------------------------------------------------------
# check checksum

csum = sum(cf[:-1]) % 256

assert csum == cf[-1], "Bad code file checksum."

# --------------------------------------------------------------
# prepare machine

print(f"Writing decomplied text to {decname}.\n")

# --------------------------------------------------------------
# decomplie

with open(decname, 'wt') as decfile:

    # icode = -1
    icode = HEADLEN - 1
    
    print(f"{'addr':4} dec (xx) {'opname':10} params")
    decfile.write(f"{'addr':4} dec (xx) {'opname':10} params\n")
    print(f"{'----':4} --- ---- {'----------':10} ------")
    decfile.write(f"{'----':4} --- ---- {'----------':10} ------\n")
    
    while icode < len(cf):
        icode += 1
        
        code = cf[icode]
        
        # show opname
        opname = code2name[code]['name']
        oplen = code2name[code]['bytes']
        
        match oplen:
            
            case 1:
                print(f"{icode:04} {code:03} ({code:02X}) {opname:10}", end=" ")
                decfile.write(f"{icode:04} {code:03} ({code:02X}) {opname:10}")
                if code == CODE_STOP or code == CODE_END:
                    break
                if code == CODE_STRING:
                    print(f"{cf[icode+1]}:{cf[icode+2:icode+2+cf[icode+1]]}", end=" ")
                    decfile.write(f"{cf[icode+1]}:{cf[icode+2:icode+2+cf[icode+1]]}")
                    icode += cf[icode+1] + 1
                print()
                decfile.write("\n")                
            
            case 2:
                print(f"{icode:04} {code:03} ({code:02X}) {opname:10} {cf[icode+1]:4}")
                decfile.write(f"{icode:04} {code:03} ({code:02X}) {opname:10} {cf[icode+1]:4}\n")
                icode += 1
            
            case 3:
                x1 = cf[icode+1]
                x2 = cf[icode+2]
                s = x1 & 128
                x1 &= 127
                x = x1 * 256 + x2
                x *= -1 if s else 1
                                
                print(f"{icode:04} {code:03} ({code:02X}) {opname:10} {cf[icode+1]:4} {cf[icode+2]:4} ({x})")
                decfile.write(f"{icode:04} {code:03} ({code:02X}) {opname:10} {cf[icode+1]:4} {cf[icode+2]:4} ({x})\n")
                icode += 2
            
            case _:
                print("???")
                decfile.write("???\n")
                
    print("\n\nJob done.\n")

# --------------------------------------------------------------
# end of code
# --------------------------------------------------------------
