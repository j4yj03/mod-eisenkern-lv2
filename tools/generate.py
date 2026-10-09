#!/usr/bin/env python3
"""Generate Eisenkern artifacts from the normative data files.

Single target: one plugin, one bundle. Emits the transformer model
includes, the LV2 bundle (manifest, mono/stereo TTL with port groups,
presets, modgui panel), the JSFX wrappers with factory presets and
RPL banks, and the generated preset documentation. Only stdlib is
required. --check compares without writing any files.

The JSFX wrappers import Eisenkern-Core.jsfx-inc and
Eisenkern-UI.jsfx-inc, which arrive with Block A3; until then the
generated wrappers are complete metadata but not loadable in REAPER.
"""
import argparse
import base64
import json
from pathlib import Path
from transformer_model import generated as transformer_files

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "https://github.com/j4yj03/mod-eisenkern-lv2#eisenkern-"
BUNDLE = 'lv2/eisenkern.lv2/'
SELECTOR_SLIDER = 14
TTL_PREFIXES = '''@prefix lv2: <http://lv2plug.in/ns/lv2core#> .
@prefix doap: <http://usefulinc.com/ns/doap#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix units: <http://lv2plug.in/ns/extensions/units#> .
@prefix pprops: <http://lv2plug.in/ns/ext/port-props#> .
@prefix pg: <http://lv2plug.in/ns/ext/port-groups#> .
@prefix mod: <http://moddevices.com/ns/mod#> .
@prefix modgui: <http://moddevices.com/ns/modgui#> .
@prefix pset: <http://lv2plug.in/ns/ext/presets#> .
'''


def number(value):
    return format(value, '.17g') if isinstance(value, float) else str(value)


def eel_number(value):
    # EEL2 does not accept C-style scientific literals in all hosts.
    text = number(value)
    if 'e' in text.lower():
        from decimal import Decimal
        text = format(Decimal(text), 'f')
    return text


def appended_value(q, preset):
    """Value an appended control takes on a preset recall.

    Oversampling resets to its default on every recall: it is a quality/CPU
    choice, not part of the transformer character. This single helper is the
    one place that decision lives (LV2 presets, JSFX presets, RPL banks).
    """
    return q['default']


def group_uri(variant, symbol):
    """Gruppen-URI: Plugin-Fragment plus Gruppen-Suffix, ein Fragment."""
    return f'{PREFIX}{variant}-group-{symbol}'


def port(index, p, variant):
    properties = []
    if p.get('labels'):
        properties += ['lv2:integer', 'lv2:enumeration']
    if p.get('toggle'):
        properties += ['lv2:integer', 'lv2:toggled']
    if p.get('integer'):
        properties.append('lv2:integer')
    if p.get('connection_optional'):
        properties += ['lv2:connectionOptional']
    lines = [f'    [ a lv2:InputPort, lv2:ControlPort; lv2:index {index};',
             f'      lv2:symbol "{p["symbol"]}"; lv2:name "{p["name"]}";']
    if p.get('group'):
        lines.append(f'      pg:group <{group_uri(variant, p["group"])}>;')
    lines += [f'      lv2:shortName "{p["short"]}"; lv2:default {number(p["default"])};',
              f'      lv2:minimum {number(p["min"])}; lv2:maximum {number(p["max"])};']
    if p.get('unit'):
        lines.append(f'      units:unit units:{p["unit"]};')
    if p.get('designation'):
        lines.append(f'      lv2:designation lv2:{p["designation"]};')
    if properties:
        lines.append('      lv2:portProperty ' + ', '.join(properties) + ';')
    for i, name in enumerate(p.get('labels', [])):
        lines.append(f'      lv2:scalePoint [ rdfs:label "{name}"; rdf:value {i} ];')
    steps = min(601, round((p['max'] - p['min']) / p['step']) + 1)
    lines.append(f'      pprops:rangeSteps {steps} ]')
    return '\n'.join(lines)


def metadata(parameters, presets, model):
    files = {}
    _, minor, micro = map(int, model['version'].split('.'))
    groups = json.loads((ROOT / 'data/port_groups.json').read_text(encoding='utf-8'))['groups']
    group_types = {g['symbol']: g.get('type', 'input') for g in groups}
    group_names = {g['symbol']: g['name'] for g in groups}
    manifest = [TTL_PREFIXES]
    gui = [TTL_PREFIXES]
    preset_text = [TTL_PREFIXES]
    for stereo in (False, True):
        variant = 'stereo' if stereo else 'mono'
        uri = PREFIX + variant
        manifest.append(f'<{uri}> a lv2:Plugin; lv2:binary <eisenkern.so>; '
                        f'rdfs:seeAlso <{variant}.ttl>, <modgui.ttl> .')
        ports = []
        audio = [('in_l', 'Input L', True), ('in_r', 'Input R', True),
                 ('out_l', 'Output L', False), ('out_r', 'Output R', False)] if stereo else [
                 ('in', 'Input', True), ('out', 'Output', False)]
        audio_group = {'in_l': 'audio_in', 'in_r': 'audio_in', 'in': 'audio_in',
                       'out_l': 'audio_out', 'out_r': 'audio_out', 'out': 'audio_out'}
        for i, (symbol, label, is_input) in enumerate(audio):
            ports.append(f'    [ a lv2:{"Input" if is_input else "Output"}Port, lv2:AudioPort; '
                         f'lv2:index {i}; lv2:symbol "{symbol}"; lv2:name "{label}"; '
                         f'pg:group <{group_uri(variant, audio_group[symbol])}> ]')
        controls = [p for p in parameters if stereo or not p.get('stereo_only')]
        existing_controls = [p for p in controls if not p.get('lv2_append')]
        appended_controls = [p for p in controls if p.get('lv2_append')]
        ports += [port(len(audio) + i, p, variant) for i, p in enumerate(existing_controls)]
        latency_index = len(audio) + len(existing_controls)
        ports.append(f'    [ a lv2:OutputPort, lv2:ControlPort; lv2:index {latency_index}; '
                     'lv2:symbol "latency"; lv2:name "Nominal latency"; '
                     'lv2:designation lv2:latency; lv2:portProperty lv2:integer, pprops:notOnGUI; '
                      'units:unit units:frame; lv2:minimum 0; lv2:maximum 32; lv2:default 0 ]')
        ports += [port(latency_index + 1 + i, p, variant) for i, p in enumerate(appended_controls)]
        # Gruppenressourcen: audio_in/audio_out plus jede referenzierte
        # Steuergruppe; Symbole muessen portfrei bleiben (pg-Spec).
        port_symbols = {s for s, _, _ in audio} | {p['symbol'] for p in controls}
        used_groups = []
        for symbol in ['audio_in', 'audio_out'] + [p['group'] for p in controls if p.get('group')]:
            if symbol not in used_groups:
                used_groups.append(symbol)
        assert not (port_symbols & set(used_groups)), port_symbols & set(used_groups)
        group_blocks = []
        for symbol in used_groups:
            if symbol == 'audio_in':
                types = ('pg:StereoGroup, ' if stereo else 'pg:MonoGroup, ') + 'pg:InputGroup'
                name = 'Input'
            elif symbol == 'audio_out':
                types = ('pg:StereoGroup, ' if stereo else 'pg:MonoGroup, ') + 'pg:OutputGroup'
                name = 'Output'
            else:
                types = 'pg:OutputGroup' if group_types[symbol] == 'output' else 'pg:InputGroup'
                name = group_names[symbol]
            group_blocks.append(
                f'<{group_uri(variant, symbol)}> a {types}; lv2:symbol "{symbol}"; '
                f'lv2:name "{name}" .')
        files[BUNDLE + variant + '.ttl'] = TTL_PREFIXES + f'''
<{uri}> a lv2:Plugin;
    doap:name "Eisenkern {variant.title()}";
    doap:license <https://opensource.org/license/mit>;
    doap:maintainer [ foaf:name "Eisenkern contributors";
        foaf:homepage <https://github.com/j4yj03/mod-eisenkern-lv2> ];
    mod:brand "GreenStripe"; mod:label "Eisenkern";
    lv2:minorVersion {minor}; lv2:microVersion {micro};
    lv2:optionalFeature lv2:hardRTCapable;
    pg:mainInput <{group_uri(variant, 'audio_in')}>;
    pg:mainOutput <{group_uri(variant, 'audio_out')}>;
    rdfs:comment "Standalone transformer: load-coupled flux core with saturation and remanence macros. Drive scales the source level into the coupled network (pure, no auto-makeup); Output is an explicit trim. No brickwall, no lookahead. Off/2x/4x oversampling, default Off, nominal latency 0/3/4 frames. Expert network parameters live in the host settings. Reduced gray-box model, not hardware calibration. The current bank derives from an input-transformer reference; the product role is intentionally neutral. See project documentation.";
    lv2:port
''' + ',\n'.join(ports) + ' .\n' + '\n'.join(group_blocks) + '\n'
        gui_ports = [p for p in controls if p['symbol'] != 'enabled']
        gui.append(f'''<{uri}> modgui:gui [
    modgui:resourcesDirectory <modgui>;
    modgui:iconTemplate <modgui/icon-{variant}.html>;
    modgui:stylesheet <modgui/eisenkern.css>;
    modgui:screenshot <modgui/screenshot-{variant}.png>;
    modgui:thumbnail <modgui/thumbnail-{variant}.png>;
    modgui:port
''' + ',\n'.join(f'    [ lv2:index {i}; lv2:symbol "{p["symbol"]}"; '
                  f'lv2:name "{p["name"]}" ]' for i, p in enumerate(gui_ports)) + ' ] .\n')
        for i, preset in enumerate(presets):
            preset_uri = PREFIX + f'preset-{variant}-{i+1:02d}'
            manifest.append(f'<{preset_uri}> a pset:Preset; lv2:appliesTo <{uri}>; '
                            f'rdfs:label "{preset["name"]}"; rdfs:seeAlso <presets.ttl> .')
            values = dict(preset, enabled=1)
            for q in appended_controls:
                values[q['symbol']] = appended_value(q, preset)
            preset_text.append(f'<{preset_uri}> a pset:Preset; lv2:appliesTo <{uri}>; '
                               f'rdfs:label "{preset["name"]}"; lv2:port\n' + ',\n'.join(
                                   f'    [ lv2:symbol "{p["symbol"]}"; pset:value {number(values[p["symbol"]])} ]'
                                   for p in controls) + ' .\n')
        files[BUNDLE + f'modgui/icon-{variant}.html'] = icon_template(stereo, parameters,
                                                                      model['version'])
    files[BUNDLE + 'manifest.ttl'] = '\n'.join(manifest) + '\n'
    files[BUNDLE + 'modgui.ttl'] = '\n'.join(gui) + '\n'
    files[BUNDLE + 'presets.ttl'] = '\n'.join(preset_text) + '\n'
    return files


def icon_template(stereo, parameters, version):
    """MOD panel after the transformer-front design (A5).

    Amp-head/variac build in HTML/CSS; design basis
    modgui/assets/transformer-front.png (element map:
    modgui/assets/README.md). Silver chassis with carry rails and feet,
    brushed purple head plate with grill slots, the EISEN selector as a
    stepped variac dial, base row with the prepared THD meter, the five
    film knobs and the power bay (bypass toggle + pilot lamp).
    Only the six panel controls are live widgets; expert controls and
    oversampling live in the host settings. Drag ring and footer plate
    follow the GS76 pattern; MOD owns control interaction/state.
    """
    def spec(symbol):
        return next(p for p in parameters if p['symbol'] == symbol)

    def screw(cls, deg):
        return (f'<i class="{cls}" aria-hidden="true">'
                f'<span class="ek-cross" style="transform:rotate({deg}deg)"></span></i>')

    def edge_labels(symbol):
        p = spec(symbol)
        lo, hi = number(p['min']), number(p['max'])
        if p.get('unit') == 'pc':
            hi += ' %'
        if p.get('unit') == 'db' and p['min'] < 0 < p['max']:
            hi = '+' + hi
        return lo, hi

    def knob(symbol, label):
        lo, hi = edge_labels(symbol)
        return (f'<div class="ek-control">'
                f'<div class="ek-knobrow"><i class="ek-scale">{lo}</i>'
                f'<div class="ek-knob" mod-role="input-control-port" mod-port-symbol="{symbol}" '
                f'mod-widget="film"></div><i class="ek-scale">{hi}</i></div>'
                f'<label>{label}</label>'
                f'<span class="ek-value" mod-role="input-control-value" mod-port-symbol="{symbol}"></span></div>')

    s = spec('eisen')
    slots = '<i class="ek-slot"></i>' * 13
    labels = ''.join(
        f'<span class="ek-model ek-model-{i}">{name}</span>'
        for i, name in enumerate(s['labels']))
    inputs = ''.join(f'<div class="ek-jack" mod-role="input-audio-port" mod-port-symbol="{x}"></div>'
                     for x in (['in_l', 'in_r'] if stereo else ['in']))
    outputs = ''.join(f'<div class="ek-jack" mod-role="output-audio-port" mod-port-symbol="{x}"></div>'
                      for x in (['out_l', 'out_r'] if stereo else ['out']))
    return f'''<!-- Generated by tools/generate.py (A5). Amp-head/variac panel after
     transformer-front.png (element map: modgui/assets/README.md). Silver
     chassis with carry rails and feet, brushed purple head plate with grill
     slots, the EISEN selector as a stepped variac dial, base row with the
     prepared THD meter, five film knobs and the power bay (bypass toggle +
     pilot lamp). Only the six panel controls are
     live widgets; expert controls and oversampling live in the host
     settings. Drag ring and footer plate; MOD owns control interaction. -->
<div class="ek{{{{{{cns}}}}}} ek-root">
<div class="mod-drag-handle ek-drag ek-drag-top" mod-role="drag-handle" title="Paneel verschieben"></div>
{screw('ek-screw ek-screw-tl', 0)}{screw('ek-screw ek-screw-tr', 45)}{screw('ek-screw ek-screw-bl', 18)}{screw('ek-screw ek-screw-br', 67)}
<div class="mod-drag-handle ek-drag ek-drag-left" mod-role="drag-handle" title="Paneel verschieben"></div>
<div class="mod-drag-handle ek-drag ek-drag-right" mod-role="drag-handle" title="Paneel verschieben"></div>
<div class="ek-bays">
<i class="ek-handle ek-handle-l" aria-hidden="true"></i><i class="ek-handle ek-handle-r" aria-hidden="true"></i>
<section class="ek-head">
{screw('ek-screw-i ek-screw-i-tl', 8)}{screw('ek-screw-i ek-screw-i-tr', 31)}{screw('ek-screw-i ek-screw-i-bl', 54)}{screw('ek-screw-i ek-screw-i-br', 79)}
<div class="ek-brand"><b>EISENKERN</b><span>TRANSFORMER</span></div>
<div class="ek-grill">{slots}</div>
<div class="ek-variac">{labels}
<div class="ek-eisen-knob" mod-role="input-control-port" mod-port-symbol="eisen" mod-widget="film" aria-label="{s['name']}"></div>
</div>
<div class="ek-presets"><label>PRESETS</label><select mod-role="presets" aria-label="Preset auswählen"><option value="">Preset auswählen</option>{{{{#effect.presets}}}}<option value="{{{{uri}}}}">{{{{label}}}}</option>{{{{/effect.presets}}}}</select></div>
</section>
<section class="ek-base">
<div class="ek-meter ek-thd-pending" title="THD-Anzeige vorbereitet; Messverfahren und Output-Port noch offen"><img class="ek-meter-face" src="/resources/assets/thd-meter-face.png{{{{{{ns}}}}}}" alt="THD"><img class="ek-meter-needle" src="/resources/assets/thd-meter-needle.png{{{{{{ns}}}}}}" alt=""><img class="ek-meter-hub" src="/resources/assets/thd-meter-hub.png{{{{{{ns}}}}}}" alt=""></div>
<div class="ek-knobs">{knob('drive', 'DRIVE')}{knob('saturation', 'SATURATION')}{knob('bass', 'BASS')}{knob('remanence', 'REMANENCE')}{knob('output', 'OUTPUT')}</div>
<div class="ek-side"><div class="ek-power"><div class="ek-bypass" mod-role="bypass" mod-widget="bypass" title="Bypass" aria-label="Bypass"></div><div class="ek-lamp" title="Betriebsanzeige"></div></div></div>
</section>
</div>
<footer>
<div class="ek-plate ek-drag-foot mod-drag-handle" mod-role="drag-handle"><b>TRANSFORMER EMULATION</b><span>{'STEREO' if stereo else 'MONO'}</span><span class="ek-plate-version">{version}</span></div>
</footer>
<div class="mod-drag-handle ek-drag ek-drag-bottom" mod-role="drag-handle" title="Paneel verschieben"></div>
<i class="ek-foot ek-foot-l" aria-hidden="true"></i><i class="ek-foot ek-foot-r" aria-hidden="true"></i>
<div class="ek-inputs">{inputs}</div><div class="ek-outputs">{outputs}</div>
</div>
'''


def jsfx_files(parameters, presets, model):
    files = {}
    appended = [p for p in parameters if p.get('jsfx_slider', 0)]
    # Sliders 1..N map to the plain control parameters in normative order; the
    # preset selector takes the next index and the appended oversampling port
    # is pinned behind it (see docs/DSP.md, Dreieck LV2/JSFX/RPL).
    selector = SELECTOR_SLIDER
    controls = [p for p in parameters if not p.get('jsfx_slider', 0)]
    assert selector == len(controls) + 1, 'selector must follow the control sliders'
    preset_eel = ['// Generated factory presets; the bank anchors hold only at neutral macros.',
                  '@init', 'function ek_apply_preset(which) (']
    for i, preset in enumerate(presets):
        preset_eel.append(f'  which=={i+1} ? (')
        values = [preset.get(p['symbol'], p['default']) for p in controls]
        preset_eel += [f'    slider{j+1}={number(x)};' for j, x in enumerate(values)]
        preset_eel += [f'    slider{q["jsfx_slider"]}={number(appended_value(q, preset))};'
                       for q in appended]
        preset_eel.append('  );')
    changed = [i + 1 for i in range(len(controls))] + [q['jsfx_slider'] for q in appended]
    mask = sum(1 << (s - 1) for s in changed)
    preset_eel += [f'  sliderchange({mask});', ');', '']
    files['jsfx/Eisenkern-Presets.jsfx-inc'] = '\n'.join(preset_eel)
    for stereo in (False, True):
        variant = 'Stereo' if stereo else 'Mono'
        rpl = [f'<REAPER_PRESET_LIBRARY "Eisenkern {variant}"']
        for preset in presets:
            # State line in slider order: controls 1..N, selector, appended.
            values = [preset.get(p['symbol'], p['default']) for p in controls]
            values += [0] + [number(appended_value(q, preset)) for q in appended]
            state = ' '.join([number(x) for x in values] + ['-']*(64-len(values)))
            payload = base64.b64encode((state + ' "' + preset['name'] + '"\x00').encode('utf-8')).decode('ascii')
            rpl += [f'  <PRESET "{preset["name"]}"', '    '+payload, '  >']
        rpl += ['>', '']
        files[f'jsfx/Eisenkern-{variant}.rpl'] = '\n'.join(rpl)
        lines = [f'desc:Eisenkern {variant}', 'author:Eisenkern contributors',
                 f'version:{model["version"]}', 'tags:transformer saturation iron colour',
                 '// SPDX-License-Identifier: MIT',
                 'options:maxmem=8192 prealloc=8192',
                 'import Eisenkern-Core.jsfx-inc',
                 'import Eisenkern-Presets.jsfx-inc',
                 'import Eisenkern-UI.jsfx-inc']
        for i, p in enumerate(parameters):
            label = p['name']
            if p.get('unit') == 'db': label += ' (dB)'
            if p.get('unit') == 'pc': label += ' (%)'
            if not stereo and p.get('stereo_only'): label = '-' + label
            labels = '{' + ','.join(p['labels']) + '}' if p.get('labels') else '{Off,On}' if p.get('toggle') else ''
            slider_index = p.get('jsfx_slider', i + 1)
            lines.append(f'slider{slider_index}:{p["default"]}<{p["min"]},'
                         f'{p["max"]},{p["step"]}{labels}>{label}')
        names = 'Custom,' + ','.join(p['name'] for p in presets)
        lines.append(f'slider{selector}:0<0,{len(presets)},1{{{names}}}>Profile preset')
        # Control sliders are derived, not hardcoded: the appended oversampling
        # port must take part in the change detection and in ek_set, or a manual
        # change would leave a stale profile preset selected.
        control_sliders = sorted(s for s in (p.get('jsfx_slider', i + 1)
                                             for i, p in enumerate(parameters)) if s)
        detect = ' || '.join(f'slider{s}!=ek_prev{s}' for s in control_sliders)
        capture = ' '.join(f'ek_prev{s}=slider{s};' for s in control_sliders)
        set_call = ','.join(f'slider{s}' for s in control_sliders)
        lines += ['in_pin:Input L', 'in_pin:Input R', 'out_pin:Output L', 'out_pin:Output R',
                  '', '@init', 'ext_nodenorm=1; ext_tail_size=-1;',
                  f'ek_stereo={1 if stereo else 0};',
                  f'#ek_ver="{model["version"]}";',
                  'ek_engine.ek_reset(ek_stereo); ek_rate=srate;',
                  f'ek_last_preset=slider{selector}; ek_have_controls=0;',
                  '', '@slider',
                  f'slider{selector}!=ek_last_preset ? (slider{selector}>0 ? '
                  f'ek_apply_preset(slider{selector}); ek_last_preset=slider{selector};) : (',
                  f'  ek_have_controls && ({detect}) ? (',
                  f'    slider{selector}=0; ek_last_preset=0; sliderchange(slider{selector});',
                  '  );', ');',
                  f'{capture} ek_have_controls=1;',
                  f'ek_engine.ek_set({set_call});',
                  '', '@block', 'srate!=ek_rate ? (',
                  '  ek_engine.ek_reset(ek_stereo); ek_rate=srate;', ');',
                  f'ek_engine.ek_set({set_call});',
                  'pdc_delay=ek_engine.ek_latency(); pdc_bot_ch=0; pdc_top_ch=2;',
                  '', '@sample',
                  'ek_rawL=ek_bound(ek_finite(spl0,0),-256,256);',
                  'ek_rawR=ek_bound(ek_finite(spl1,0),-256,256);',
                  'ek_stereo ? ek_engine.ek_process(ek_rawL,ek_rawR) : '
                  'ek_engine.ek_process(ek_rawL,ek_rawL);',
                  'spl0=ek_engine.outL; spl1=ek_engine.outR;', '']
        files[f'jsfx/Eisenkern-{variant}.jsfx'] = '\n'.join(lines)
    # Labels come from the normative parameter data so docs cannot drift.
    model_names = next(p['labels'] for p in parameters if p['symbol'] == 'eisen')
    family_names = next(p['labels'] for p in parameters if p['symbol'] == 'family')
    docs = ['# Eisenkern — Factory Profiles', '',
            '> Four profiles as own voicing, not hardware measurements.',
            '> The 1-%-THD anchors (−14/−8/−2 dBFS) hold only at neutral macros',
            '> (Drive 0 dB, Saturation/Remanence 100 %, Bass 1.0).',
            '> Oversampling is a separate quality/CPU choice and always recalls to Off.', '',
            '| Preset | Eisen | Drive / Output dB | Saturation / Remanence % | Bass | Load / Source Ω | HF corner Hz / Q | Family / Exponent |',
            '|---|---|---|---|---|---|---|---|']
    for p in presets:
        docs.append(
            f'| {p["name"]} | {model_names[p["eisen"]]} | {p["drive"]} / {p["output"]} | '
            f'{p["saturation"]} / {p["remanence"]} | {p["bass"]} | '
            f'{p["load"]} / {p["source"]} | {number(p["hf_frequency"])} / {number(p["hf_q"])} | '
            f'{family_names[p["family"]]} / {p["exponent"]} |')
    for p in presets:
        docs += ['', f'## {p["name"]}', '', p['note'], '']
    files['docs/PRESETS.md'] = '\n'.join(docs) + '\n'
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    # read_text() without an encoding uses the locale encoding, which on Windows
    # is cp1252 and mangles UTF-8 content in data/*.json.
    model = json.loads((ROOT/'data/model.json').read_text(encoding='utf-8'))
    parameters = json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    presets = json.loads((ROOT/'data/presets.json').read_text(encoding='utf-8'))
    transformers = json.loads((ROOT/model['transformer_bank']).read_text(encoding='utf-8'))
    labels = next(p['labels'] for p in parameters if p['symbol'] == 'eisen')
    if labels != list(transformers['profiles']):
        raise ValueError('Model port labels and runtime bank order disagree')
    files = dict(metadata(parameters, presets, model), **jsfx_files(parameters, presets, model))
    files.update(transformer_files(transformers, number, eel_number))
    mismatch = []
    for path, text in files.items():
        destination = ROOT/path
        if args.check:
            if not destination.exists() or destination.read_text(encoding='utf-8') != text:
                mismatch.append(path)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Not Path.write_text(newline=...): that keyword only exists from
            # Python 3.10 on, and this generator has to run on the test machine,
            # which is on 3.9. Opening with newline='' writes the bytes as given
            # on every version, so the generated files keep LF everywhere.
            with destination.open('w', encoding='utf-8', newline='') as handle:
                handle.write(text)
    if mismatch:
        raise SystemExit('Generated files are stale: ' + ', '.join(mismatch))
    print(f'{"Verified" if args.check else "Generated"} {len(files)} files')


if __name__ == '__main__':
    main()
