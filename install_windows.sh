echo "This only functions within the windows mingw64 terminal / system. You can download them here. https://www.msys2.org/"
pacman -S mingw-w64-x86_64-python-matplotlib
pacman -S mingw-w64-x86_64-python-scikit-learn
pacman -S mingw-w64-x86_64-gobject-introspection
pacman -S mingw-w64-x86_64-python-gobject
pacman -S mingw-w64-x86_64-gtk4
pacman -S mingw-w64-x86_64-python-seaborn
/mingw64/bin/python main.py
