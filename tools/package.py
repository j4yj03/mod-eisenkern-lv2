#!/usr/bin/env python3
"""Build auditable JSFX/source/native-LV2 packages; no external model data."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def zip_package(destination,files):
    manifest=[]
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path,relative in sorted(files,key=lambda item:item[1]):
            archive.write(path,relative)
            manifest.append(dict(path=relative,sha256=sha(path),bytes=path.stat().st_size))
        archive.writestr('PACKAGE-MANIFEST.json',json.dumps(manifest,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path)
    parser.add_argument('--dwarf',action='store_true',help='Require AArch64/glibc<=2.27 before labelling Dwarf')
    parser.add_argument('--toolchain',default='Unspecified; see external build report')
    parser.add_argument('--output',type=Path,default=ROOT/'dist')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
# read_text() without an encoding uses the locale encoding, which on Windows
#     is cp1252 and mangles the UTF-8 dashes in data/*.json.
    version=json.loads((ROOT/'data/model.json').read_text(encoding='utf-8'))['version']
    jsfx=[(p,'Eisenkern/'+p.name) for p in (ROOT/'jsfx').iterdir() if p.is_file()]
    jsfx += [(ROOT/'LICENSE','Eisenkern/LICENSE'),(ROOT/'docs/PRESETS.md','Eisenkern/PRESETS.md'),
             (ROOT/'docs/MESSTECHNIK.md','Eisenkern/MESSTECHNIK.md'),
             (ROOT/'docs/DSP.md','Eisenkern/DSP.md'),
             (ROOT/'data/transformers.json','Eisenkern/transformers.json')]
    zip_package(args.output/f'eisenkern-{version}-jsfx.zip',jsfx)
    source=[]
    excluded={'.git','build','dist','.deps','__pycache__','test-results'}
    for p in ROOT.rglob('*'):
        relative=p.relative_to(ROOT)
        if p.is_file() and not any(x in excluded for x in relative.parts) and p.suffix.lower() not in ('.nam','.wav','.pyc','.so','.pdf','.npz'):
            source.append((p,'eisenkern/'+str(relative)))
    zip_package(args.output/f'eisenkern-{version}-source.zip',source)
    if args.bundle:
        from check_abi import inspect
        binary=args.bundle/'eisenkern.so'
        if not binary.is_file(): raise SystemExit('Missing compiled bundle binary')
        abi=inspect(binary)
        if args.dwarf:
            if abi['machine']!='AArch64' or any(tuple(map(int,v.split('.')))>(2,27) for v in abi['versions']['GLIBC']):
                raise SystemExit('Cannot label incompatible binary as Dwarf')
        tag='moddwarf' if args.dwarf else 'native-'+abi['machine'].replace(' ','-').replace('/','-')
        archivePath=args.output/f'eisenkern-{version}-{tag}.tar.gz'
        with tarfile.open(archivePath,'w:gz') as archive:
            archive.add(args.bundle,arcname='eisenkern.lv2')
        report=dict(binary_sha256=sha(binary),abi=abi,toolchain=args.toolchain,device_tested=False)
        archivePath.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    checksums=[f'{sha(p)}  {p.name}' for p in sorted(args.output.iterdir()) if p.is_file() and p.name!='SHA256SUMS']
    (args.output/'SHA256SUMS').write_text('\n'.join(checksums)+'\n')
    print('Packages written to '+str(args.output))


if __name__=='__main__': main()
