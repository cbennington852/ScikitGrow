glib-compile-resources reasources.xml --target=resources.gresource
source .venv/bin/activate
GSK_RENDERER=ngl python3 main.py