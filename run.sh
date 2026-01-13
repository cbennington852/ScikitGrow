source ./myenv/bin/activate
pyrcc5 -o src/image_resources.py resources/resources.qrc
#python main.py resources/iris.csv
python3 -m src.main