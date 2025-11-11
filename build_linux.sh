pyinstaller --onefile \
 --hidden-import=gi.repository \
  --hidden-import=matplotlib.backends.backend_gtk4agg \
  --hidden-import=gi._gi_cairo \
  --hidden-import=gi.repository.Gtk \
   main.py