# Eisenkern — native build and offline checks.
# The DSP translation units arrive with Block A2 (src/lv2_plugin.cpp);
# until then `make`/`make build` reports the pending block and the
# offline checks are the verification path.

CXX ?= c++
PYTHON ?= python3
BUILD_DIR ?= build/native
CPPFLAGS += -Isrc
CXXFLAGS += -O3
PROJECT_CXXFLAGS = -std=c++11 -Wall -Wextra -Wpedantic -fPIC -fvisibility=hidden -fno-fast-math -ffp-contract=off
LDFLAGS += -Wl,--no-undefined
LIBRARY = $(BUILD_DIR)/eisenkern.lv2/eisenkern.so
HEADERS = $(wildcard src/dsp/*.hpp) src/lv2_abi.h

.PHONY: all build generate check-generated test clean

all: build

generate:
	$(PYTHON) tools/generate.py

check-generated:
	$(PYTHON) tools/generate.py --check

build:
	@test -f src/lv2_plugin.cpp || { \
		echo "DSP-Wrapper fehlt (Block A2): src/lv2_plugin.cpp — der LV2-Build folgt mit A2."; exit 1; }
	mkdir -p "$(BUILD_DIR)/eisenkern.lv2"
	cp -R lv2/eisenkern.lv2/. "$(BUILD_DIR)/eisenkern.lv2/"
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(PROJECT_CXXFLAGS) -fno-exceptions -fno-rtti -shared src/lv2_plugin.cpp $(LDFLAGS) -o "$(LIBRARY)"

test: check-generated
	$(PYTHON) tools/validate.py

clean:
	rm -rf "$(BUILD_DIR)"
