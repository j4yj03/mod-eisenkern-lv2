#!/usr/bin/env python3
"""One-time transfer verification: Eisenkern against mod-1175-lv2 (GS76).

Compares, against ../mod-1175-lv2 (or $GS76_ROOT):
1. data/transformers.json — every profile field and stop threshold exactly
   equal (floats compared as parsed doubles, i.e. bit-identical values).
2. Generated src/dsp/TransformerModels.hpp — profile rows and threshold
   tokens identical (guard/namespace/provenance comments differ by design).
3. Generated jsfx/Eisenkern-Transformers.jsfx-inc — dest[j]=<value> and
   threshold tokens identical (function names ek_* vs gs_* by design).

Temporary tool of the code separation; it can be removed once the own
A4 test suite carries its own references. Exits non-zero on any deviation.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GS76 = Path(os.environ.get('GS76_ROOT', ROOT.parent/'mod-1175-lv2'))


def failures():
    problems = []
    ours = json.loads((ROOT/'data/transformers.json').read_text(encoding='utf-8'))
    theirs = json.loads((GS76/'data/transformers.json').read_text(encoding='utf-8'))
    if ours['stop_thresholds_vs'] != theirs['stop_thresholds_vs']:
        problems.append('stop thresholds differ')
    for name, profile in theirs['profiles'].items():
        if name not in ours['profiles']:
            problems.append(f'profile {name} missing')
            continue
        for key, value in profile.items():
            if ours['profiles'][name].get(key) != value:
                problems.append(f'{name}/{key}: {ours["profiles"][name].get(key)!r} != {value!r}')
    if ours['source_sha256'] != theirs['source_sha256']:
        problems.append('source_sha256 differs')
    if ours['source_fit_sha256'] != theirs['source_fit_sha256']:
        problems.append('source_fit_sha256 differs')
    if ours['source_revision'] != theirs['revision']:
        problems.append('source_revision does not point at the GS76 revision')

    ours_hpp = (ROOT/'src/dsp/TransformerModels.hpp').read_text(encoding='utf-8')
    theirs_hpp = (GS76/'src/dsp/TransformerModels.hpp').read_text(encoding='utf-8')
    ours_rows = re.findall(r'^    \{(.*)\},$', ours_hpp, re.M)
    theirs_rows = re.findall(r'^    \{(.*)\},$', theirs_hpp, re.M)
    if ours_rows != theirs_rows:
        problems.append('TransformerModels.hpp profile rows differ')
    ours_thr = re.search(r'thresholds\[\] = \{(.*)\};', ours_hpp)
    theirs_thr = re.search(r'thresholds\[\] = \{(.*)\};', theirs_hpp)
    if not ours_thr or not theirs_thr or ours_thr.group(1) != theirs_thr.group(1):
        problems.append('TransformerModels.hpp thresholds differ')

    ours_eel = (ROOT/'jsfx/Eisenkern-Transformers.jsfx-inc').read_text(encoding='utf-8')
    theirs_eel = (GS76/'jsfx/GreenStripe76-Transformers.jsfx-inc').read_text(encoding='utf-8')
    ours_values = re.findall(r'dest\[\d+\]=([^;]+);', ours_eel)
    theirs_values = re.findall(r'dest\[\d+\]=([^;]+);', theirs_eel)
    if ours_values != theirs_values:
        for index, (a, b) in enumerate(zip(ours_values, theirs_values)):
            if a != b:
                problems.append(f'jsfx token {index}: {a} != {b}')
        if len(ours_values) != len(theirs_values):
            problems.append(f'jsfx token count {len(ours_values)} != {len(theirs_values)}')
    return problems


def main():
    if not GS76.is_dir():
        raise SystemExit(f'sibling repository not found: {GS76}')
    problems = failures()
    if problems:
        for problem in problems:
            print('FAIL ' + problem)
        raise SystemExit(f'Transfer verification FAILED: {len(problems)} deviations')
    print('Transfer verification PASS: bank, thresholds and generated constants '
          f'bit-identical against {GS76}')


if __name__ == '__main__':
    main()
