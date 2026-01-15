---
title: 'DataScratch : A drag and drop interface for data science'
tags:
  - Python
  - Data Science
  - Statistics
authors:
  - name: Charles Bennington
    orcid: 0009-0005-0682-163X
    equal-contrib: true
    affiliation: "1" # (Multiple affiliations must be quoted)
affiliations:
 - name: Department of Computer Science, Gonzaga University, USA
   index: 1
date: 13 January 2026
bibliography: paper.bib
---
<!--
Important Notes: 
    Length : 250 words - 1,000 words

-->

# Summary
Data science is a current and evolving field. Currently, this field is historicity a extremely coding heavy field. DataScratch is a novel approach to perform data science tasks, such as model training, and validation, through drag and drop interface. 

# Statement of need


# State of the field

# Software design
The language for this software is python, this is because python possesses several libraries, such as pandas[CITATION], matplotlib[CITATION], and scikit-learn[CITATION], which are standard to any data science process. 

The GUI software was originally written using a python library called PyGtk[CITATION], however after several months of development this library was dropped, due to the PyGtk library having a non-functional pip installation, and graphical issues when run on windows. The project later switched to PyQt, which featured cross platform support, and allowed for installation via pip by default.

The drag and drop components are modeled closely after scratch[CITATION], a library which has been shown to be very intuitive and easy to use[CITATION]. This choice was intended to make the software easier to use for people who aren't heavy coders. 
![blocks v python](paper_images/Python_v_datascratch.svg "Image showing the complexity of coding versus the new drag and drop interface.")

The interface also enables the user to assemble and train multiple models at once, allowing for quick model comparison.


# Research impact statement



# AI usage disclosure
The dataframe_viewer class was heavily written by AI. This is a small subclass which renders a pandas dataframe as a PyQt table. Google was used to search for API documentation. The built in AI overview on google cannot be deactivated, and thus the AI overview was unintentionally used upon each google search. Oftentimes, the AI overview provided false information, and was later ignored due to a lack of verifiability. 





# Citations
