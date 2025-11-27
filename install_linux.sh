sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0
python -m venv .venv
source .venv/bin/activate
pip install scikit-learn matplotlib numpy 
pip3 install pycairo
glib-compile-resources reasources.xml --target=resources.gresource
