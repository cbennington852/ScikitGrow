brew install pygobject3 gtk4
glib-compile-resources reasources.xml --target=resources.gresource
python -m venv .venv
source .venv/bin/activate
pip install scikit-learn matplotlib numpy 
