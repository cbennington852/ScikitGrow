source ./myenv/bin/activate
pyrcc5 -o src/image_resources.py resources/resources.qrc
pip install -e .