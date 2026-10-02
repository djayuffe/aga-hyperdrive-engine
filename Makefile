PYTHON ?= python3
VASM ?= $(shell command -v vasmm68k_mot 2>/dev/null || true)
LOCAL_VASM := tools/bin/vasmm68k_mot
VASMFLAGS = -m68000 -kick1hunks -Fhunkexe -nosym -I./src -I.
TARGET = build/aga_hyperdrive_engine
SRCS = src/main.s src/hardware.i
ASSET_STAMP = assets/.generated

all: $(TARGET)

$(ASSET_STAMP): tools/generate_assets.py tools/gen_tables.py
	@mkdir -p assets
	$(PYTHON) tools/generate_assets.py
	@touch $@

assets: $(ASSET_STAMP)

validate: $(ASSET_STAMP)
	$(PYTHON) tools/validate.py

verify-repro: $(ASSET_STAMP)
	$(PYTHON) tools/verify_repro.py

$(TARGET): $(ASSET_STAMP) $(SRCS) | build
	@if [ -n "$(VASM)" ]; then A="$(VASM)"; elif [ -x "$(LOCAL_VASM)" ]; then A="$(LOCAL_VASM)"; else echo "No VASM. Install vasmm68k_mot or copy it to tools/bin/vasmm68k_mot."; exit 2; fi; \
	$$A $(VASMFLAGS) -o $(TARGET) src/main.s

build:
	mkdir -p build

manifest:
	$(PYTHON) tools/make_manifest.py

clean:
	rm -rf build

.PHONY: all assets validate verify-repro manifest clean
