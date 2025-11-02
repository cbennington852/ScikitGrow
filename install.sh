glib-compile-resources reasources.xml --target=resources.gresource
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt