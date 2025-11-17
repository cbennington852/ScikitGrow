echo This required WSL to be installed on the system first!
wsl --install Ubuntu-24.04
wsl sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0
wsl sudo python -m venv .venv
wsl sudo source .venv/bin/activate
wsl sudo pip install scikit-learn matplotlib numpy 
wsl sudo pip3 install pycairo