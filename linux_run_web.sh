glib-compile-resources reasources.xml --target=resources.gresource
source .venv/bin/activate
GDK_BACKEND=broadway BROADWAY_DISPLAY=:5  python3 main.py example_datasets/iris.csv