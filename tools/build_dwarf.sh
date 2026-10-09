#!/usr/bin/env bash
# Run INSIDE an official MOD Plugin Builder environment; does not deploy.
set -euo pipefail
ROOT="$(realpath "$(dirname "$0")/..")"
MPB_ROOT="${MPB_ROOT:-/root/mod-plugin-builder}"
if [[ ! -f "$MPB_ROOT/local.env" ]]; then
    printf 'Missing MOD Plugin Builder local.env at %s\n' "$MPB_ROOT" >&2
    exit 1
fi
# Upstream environment script does not guarantee nounset-safe variables.
set +u
source "$MPB_ROOT/local.env" moddwarf-new
set -u
if [[ "${CXX:-}" != aarch64-modaudio-linux-gnu-g++ ]]; then
    printf 'Unexpected MOD Dwarf compiler: %s\n' "${CXX:-unset}" >&2
    exit 1
fi
make -C "$ROOT" BUILD_DIR=build/moddwarf
python3 "$ROOT/tools/check_abi.py" "$ROOT/build/moddwarf/eisenkern.lv2/eisenkern.so" --dwarf
python3 "$ROOT/tools/package.py" --bundle "$ROOT/build/moddwarf/eisenkern.lv2" --dwarf \
    --toolchain "MPB moddwarf-new: $(git -C "$MPB_ROOT" rev-parse HEAD); $($CXX -dumpfullversion)"
