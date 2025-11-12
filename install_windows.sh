pacman -Suy
pacman -S mingw-w64-ucrt-x86_64-gtk4 mingw-w64-ucrt-x86_64-python3 mingw-w64-ucrt-x86_64-python3-gobject --noconfirm
pacman -S python --noconfirm
pacman -S python-pip --noconfirm
python -m venv .venv
source .venv/bin/activate
pip install scikit-learn numpy matplotlib
glib-compile-resources reasources.xml --target=resources.gresource
pacman -Su