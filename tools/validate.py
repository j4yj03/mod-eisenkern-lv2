#!/usr/bin/env python3
"""Validate the normative data files and the generated bundle structure.

Scope: transformer bank (schema/provenance/limits), model.json sanity,
parameter/port-group consistency, preset semantics, and structural checks
of the generated TTLs (port counts, group references, Mono/Stereo types,
mainInput/mainOutput). Full RDF parsing runs on the test machine (rdflib);
artifact freshness stays with `tools/generate.py --check`.

JSFX imports of Eisenkern-Core.jsfx-inc and Eisenkern-UI.jsfx-inc are
reported as pending (Block A3/A5), not failed — the wrappers are complete
metadata before the engines land.
"""
import json
import re
from pathlib import Path
from transformer_model import validate

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'https://github.com/j4yj03/mod-eisenkern-lv2#eisenkern-'
EXPECTED_GROUPS = ('core', 'level', 'expert', 'system', 'audio_in', 'audio_out')


def fail(message):
    raise SystemExit('validate: ' + message)


def check_model(model):
    if not re.fullmatch(r'\d+\.\d+\.\d+', str(model.get('version', ''))):
        fail('model.json: version must be three-part (revision is the third part)')
    if not str(model.get('calibration_status', '')).strip():
        fail('model.json: calibration_status required')
    bank_path = ROOT/model.get('transformer_bank', '')
    if not bank_path.is_file():
        fail('model.json: transformer_bank file missing')
    for key in ('oversampling', 'default_oversampling',
                'latency_2x_frames', 'nominal_latency_frames'):
        value = model.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            fail(f'model.json: {key} must be a non-negative integer')
    if model['default_oversampling'] != 0:
        fail('model.json: default_oversampling must be Off (0), like GS76')
    return bank_path


def check_parameters(parameters, groups, bank):
    symbols = [p['symbol'] for p in parameters]
    if len(set(symbols)) != len(symbols):
        fail('parameters: duplicate symbols')
    group_symbols = {g['symbol'] for g in groups}
    if group_symbols & set(symbols):
        fail(f'pg namespace shared with ports: {group_symbols & set(symbols)}')
    for p in parameters:
        for key in ('symbol', 'name', 'short', 'default', 'min', 'max', 'step'):
            if key not in p:
                fail(f'{p.get("symbol")}: missing {key}')
        if not p['min'] < p['max']:
            fail(f'{p["symbol"]}: min must be below max')
        if not p['min'] <= p['default'] <= p['max']:
            fail(f'{p["symbol"]}: default outside [{p["min"]}, {p["max"]}]')
        if p['step'] <= 0:
            fail(f'{p["symbol"]}: step must be positive')
        if p.get('group') and p['group'] not in group_symbols:
            fail(f'{p["symbol"]}: unknown group {p["group"]}')
        if p.get('designation') == 'enabled' and p.get('group'):
            pass  # Eisenkern keeps enabled inside the System group by plan.
    model_port = parameters[0]
    if model_port['symbol'] != 'eisen':
        fail('parameters: first control must be the profile selector (eisen)')
    if model_port['labels'] != list(bank['profiles']):
        fail('eisen labels and runtime bank order disagree')
    appended = [p for p in parameters if p.get('lv2_append')]
    if [p['symbol'] for p in appended] != ['oversampling']:
        fail('exactly oversampling must be lv2_append')
    for p in appended:
        if not p.get('connection_optional') or not p.get('jsfx_slider'):
            fail('oversampling: appended port needs connectionOptional and a JSFX slider')
    sliders = []
    for i, p in enumerate(parameters):
        sliders.append(p.get('jsfx_slider', i + 1))
    if len(set(sliders)) != len(sliders) or 0 in sliders:
        fail(f'jsfx slider assignment collides: {sorted(sliders)}')
    controls = [p for p in parameters if not p.get('jsfx_slider', 0)]
    if sorted(sliders) != list(range(1, len(controls) + 1)) + \
            [p['jsfx_slider'] for p in appended]:
        fail('jsfx sliders must be 1..N for controls, appended ports pinned behind the selector')
    if max(s for s in sliders) != len(controls) + 1 + len(appended):
        fail('the oversampling slider must sit directly behind the preset selector')
    os_port = next(p for p in parameters if p['symbol'] == 'oversampling')
    if os_port['labels'] != ['Off', '2x', '4x'] or os_port['default'] != 0:
        fail('oversampling: labels Off/2x/4x and default Off are normative')
    enabled = next(p for p in parameters if p['symbol'] == 'enabled')
    if not enabled.get('toggle') or enabled.get('designation') != 'enabled':
        fail('enabled: toggle with lv2:designation enabled is normative')
    return controls, appended


def check_presets(presets, parameters, bank):
    names = [p['name'] for p in presets]
    if len(set(names)) != len(names):
        fail('presets: duplicate names')
    model_labels = list(bank['profiles'])
    models = sorted(p['eisen'] for p in presets)
    if models != list(range(len(model_labels))):
        fail('presets: the four factory presets must cover every profile exactly once')
    for preset in presets:
        for p in parameters:
            if p.get('lv2_append'):
                continue  # appended ports are not preset-adressable values here
            if p['symbol'] == 'enabled':
                continue
            value = preset.get(p['symbol'], p['default'])
            if not p['min'] <= value <= p['max']:
                fail(f'{preset["name"]}/{p["symbol"]}: {value} outside '
                     f'[{p["min"]}, {p["max"]}]')
        if preset.get('oversampling', 0) != 0:
            fail(f'{preset["name"]}: oversampling must recall to Off')
        if preset.get('enabled', 1) != 1:
            fail(f'{preset["name"]}: factory presets are enabled')


def check_ttl(bank):
    problems = []
    for variant, audio, group_kind in (('mono', 2, 'MonoGroup'), ('stereo', 4, 'StereoGroup')):
        text = (ROOT/f'lv2/eisenkern.lv2/{variant}.ttl').read_text(encoding='utf-8')
        audio_count = text.count('lv2:AudioPort')
        if audio_count != audio:
            problems.append(f'{variant}.ttl: {audio_count} audio ports')
        inputs = text.count('a lv2:InputPort, lv2:ControlPort')
        outputs = text.count('a lv2:OutputPort, lv2:ControlPort')
        if (inputs, outputs) != (14, 1):
            problems.append(f'{variant}.ttl: {inputs} control inputs, {outputs} control outputs')
        if 'lv2:designation lv2:latency' not in text:
            problems.append(f'{variant}.ttl: latency designation missing')
        if f'pg:mainInput <{PREFIX}{variant}-group-audio_in>' not in text or \
                f'pg:mainOutput <{PREFIX}{variant}-group-audio_out>' not in text:
            problems.append(f'{variant}.ttl: mainInput/mainOutput missing')
        used = set(re.findall(r'pg:group <' + re.escape(PREFIX) +
                              variant + r'-group-([a-z_]+)>', text))
        if used - set(EXPECTED_GROUPS):
            problems.append(f'{variant}.ttl: unexpected groups {used - set(EXPECTED_GROUPS)}')
        defined = set(re.findall(r'<' + re.escape(PREFIX) + variant +
                                 r'-group-([a-z_]+)> a ', text))
        if used != defined:
            problems.append(f'{variant}.ttl: groups used {sorted(used)} vs defined {sorted(defined)}')
        if text.count(f'a pg:{group_kind}, pg:InputGroup') != 1 or \
                text.count(f'a pg:{group_kind}, pg:OutputGroup') != 1:
            problems.append(f'{variant}.ttl: audio group types wrong for {variant}')
    presets_text = (ROOT/'lv2/eisenkern.lv2/presets.ttl').read_text(encoding='utf-8')
    if presets_text.count('a pset:Preset;') != 2 * len(bank['profiles']):
        problems.append('presets.ttl: unexpected preset count')
    if 'pset:value' in presets_text and 'gr_db' in presets_text:
        problems.append('presets.ttl: output ports must not be preset-adressable')
    manifest = (ROOT/'lv2/eisenkern.lv2/manifest.ttl').read_text(encoding='utf-8')
    if manifest.count('a lv2:Plugin;') != 2:
        problems.append('manifest.ttl: expected exactly two plugins')
    return problems


def main():
    model = json.loads((ROOT/'data/model.json').read_text(encoding='utf-8'))
    bank_path = check_model(model)
    bank = json.loads(bank_path.read_text(encoding='utf-8'))
    validate(bank)
    parameters = json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    groups = json.loads((ROOT/'data/port_groups.json').read_text(encoding='utf-8'))['groups']
    presets = json.loads((ROOT/'data/presets.json').read_text(encoding='utf-8'))
    check_parameters(parameters, groups, bank)
    check_presets(presets, parameters, bank)
    problems = check_ttl(bank)
    if problems:
        for problem in problems:
            print('FAIL ' + problem)
        raise SystemExit(f'validate: {len(problems)} structural problems')
    for include in ('Eisenkern-Core.jsfx-inc', 'Eisenkern-UI.jsfx-inc'):
        if not (ROOT/'jsfx'/include).exists():
            print(f'Note: jsfx/{include} pending (Block A3/A5); wrapper not loadable yet')
    print(f"Validated bank {bank['revision']} ({bank_path.name}); model {model['version']}; "
          f'{len(presets)} presets, 2 variants, port counts OK')


if __name__ == '__main__':
    main()
