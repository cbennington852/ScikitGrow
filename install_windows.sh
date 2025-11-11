pacman -Suy
pacman -S mingw-w64-ucrt-x86_64-gtk4 mingw-w64-ucrt-x86_64-python3 mingw-w64-ucrt-x86_64-python3-gobject
sudo pacman -S python-pip
pip install -r requirements.txt
glib-compile-resources reasources.xml --target=resources.gresource
python -m venv .venv
source .venv/bin/activate