source ./myenv/bin/activate
pyrcc5 -o image_resources.py images/resources.qrc
python main.py example_datasets/test.csv