glib-compile-resources reasources.xml --target=resources.gresource
source .venv/bin/activate
gtk4-broadwayd :5 -p 8085 &
GDK_BACKEND=broadway BROADWAY_DISPLAY=:5  python3 main.py example_datasets/iris.csv
echo "Server live on http://127.0.0.1:8085/"