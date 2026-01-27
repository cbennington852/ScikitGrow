source ./myenv/bin/activate
python clear_saved_app_data.py
pyrcc5 -o src/datascratch/image_resources.py resources/resources.qrc
pip install -e .
