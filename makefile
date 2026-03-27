VENV_FOLDER = ./venv_qif
PYTHON = $(VENV_FOLDER)/bin/python

install:
	mkdir -p $(VENV_FOLDER)
	python3 -m venv $(VENV_FOLDER)
	. $(VENV_FOLDER)/bin/activate && $(PYTHON) -m pip install -r requirements.txt

build_3d:
	$(PYTHON) -m 3d_plot.generate_3d_explorer