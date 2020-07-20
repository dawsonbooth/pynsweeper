SOURCE = src/main.py

VERSION := $(shell poetry version | grep -oE '[^ ]+$$')

PLATFORM :=
DATA :=
ICON :=
ifeq ($(OS),Windows_NT)
	PLATFORM = win32
	DATA = "assets;assets"
	ICON = assets/ico/icon.ico
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		PLATFORM = linux
		DATA = "assets:assets"
		ICON = assets/ico/icon.icns
	endif
	ifeq ($(UNAME_S),Darwin)
		PLATFORM = darwin
		DATA = "assets:assets"
		ICON = assets/ico/icon.ico
	endif
endif

FILENAME = pynsweeper-$(VERSION)-$(PLATFORM)

BUILDFLAGS = --onefile --windowed --name $(FILENAME) --icon $(ICON) --add-data $(DATA)

.PHONY: all list clean release build version

all: list

list:
	@sh -c "$(MAKE) -p no_targets__ | \
		awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {\
			split(\$$1,A,/ /);for(i in A)print A[i]\
		}' | grep -v '__\$$' | grep -v 'make\[1\]' | grep -v 'Makefile' | sort"

clean:
	rm -rf build/ dist/ **/__pycache__/
	rm -f *.spec **/*.pyc

release:
	git tag v$(VERSION)
	git push origin v$(VERSION)

build: clean
	@poetry run pyinstaller $(BUILDFLAGS) $(SOURCE)

version:
	@echo $(VERSION)
