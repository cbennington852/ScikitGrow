import PyQt5.QtWidgets as QtW 
from PyQt5.QtWidgets import QWidget


def end_drag_and_drop_event(to_parent : QWidget , from_parent : QWidget):
	"""
		Small utility function to handle universally drag and drop things.

		This calls some of the functions nessicary to drag and drop if the corresponding widgets have those.
	"""
	# 1. Resizing 
	if hasattr(from_parent , "resize_based_on_children"):
		print("From parent resized")
		from_parent.resize_based_on_children()
	if hasattr(to_parent , "resize_based_on_children"):
		print("From parent resized")
		to_parent.resize_based_on_children()
	if hasattr(to_parent , "my_parent"):
		if hasattr(to_parent.my_parent , "resize_based_on_children"):
			to_parent.my_parent.resize_based_on_children()
	if hasattr(from_parent , "my_parent"):
		if hasattr(from_parent.my_parent , "resize_based_on_children"):
			from_parent.my_parent.resize_based_on_children()

	# 2. repainting
	to_parent.repaint()
	from_parent.repaint()
	print("End found")

def is_holding(curr_parent : QWidget) -> bool:
	"""Check if it's holding things

	Args:
		curr_parent (QWidget): _description_

	Returns:
		bool: _description_
	"""
	for child in curr_parent.findChildren(QtW.QWidget):
		return True
	return False

