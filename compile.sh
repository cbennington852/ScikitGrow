source ./myenv/bin/activate
pyrcc5 -o src/datascratch/image_resources.py resources/resources.qrc
pip install -e .