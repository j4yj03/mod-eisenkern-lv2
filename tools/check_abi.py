#!/usr/bin/env python3
"""Inspect ELF dependencies and version floors; --dwarf gates obvious mistakes."""
import argparse
import json
from pathlib import Path
import re
import subprocess


def inspect(binary, readelf='readelf'):
    outputs={flag:subprocess.check_output([readelf,flag,str(binary)],text=True) for flag in ('-h','-d','--version-info')}
    machine=re.search(r'Machine:\s*(.+)',outputs['-h']).group(1).strip()
    needed=re.findall(r'\(NEEDED\).*?\[(.+?)\]',outputs['-d'])
    versions={kind:sorted(set(re.findall(kind+r'_([0-9.]+)',outputs['--version-info'])),key=lambda s:tuple(map(int,s.split('.')))) for kind in ('GLIBC','GLIBCXX','CXXABI')}
    return dict(machine=machine,needed=needed,versions=versions)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary',type=Path)
    parser.add_argument('--dwarf',action='store_true')
    parser.add_argument('--readelf',default='readelf')
    args=parser.parse_args(); result=inspect(args.binary,args.readelf)
    print(json.dumps(result,indent=2))
    if args.dwarf:
        if result['machine']!='AArch64': raise SystemExit('Not an AArch64 plugin')
        if any(tuple(map(int,v.split('.')))>(2,27) for v in result['versions']['GLIBC']):
            raise SystemExit('Requires glibc newer than MOD target 2.27')
        if any('X11' in x or 'webkit' in x.lower() or 'Qt' in x for x in result['needed']):
            raise SystemExit('Unexpected GUI runtime dependency')
        print('Dwarf ELF/GLIBC floor: PASS (still requires real firmware load test)')


if __name__=='__main__': main()
