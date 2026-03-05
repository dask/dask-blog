.PHONY: build serve clean

build:
	sphinx-build -b dirhtml . _build/dirhtml

serve:
	sphinx-autobuild . _build/dirhtml -b dirhtml --open-browser

clean:
	rm -rf _build .doctrees
