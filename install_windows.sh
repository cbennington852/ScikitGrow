pacman -Suy
pacman -S mingw-w64-ucrt-x86_64-gtk4 mingw-w64-ucrt-x86_64-python3 mingw-w64-ucrt-x86_64-python3-gobject --noconfirm
pacman -S python --noconfirm
pacman -S python-pip --noconfirm
pip install scikit-learn matplotlib numpy 
glib-compile-resources reasources.xml --target=resources.gresource
pacman -Su