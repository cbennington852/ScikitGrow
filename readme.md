---
title: 'DataScratch : A drag and drop interface to build AI models'
tags:
  - Python
  - Data Science
  - Statistics
  - AI
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

![blocks v python](resources/Full_logo_SciKit_Grow.svg "Optional title text")

## Background & Inspiration

Invented in 2003 scratch is a programming language intended for children ages 10 - 15. The intent of this project was to model programming concepts via large colorful blocks, to teach children the basics of programming. Scratch has since been a massive success, as of 2023 scratch go 95 million monthly visits, some fo those recurring users, other programming novices. 

This language was intended to model real world programming, whilst giving children a streamlined experience, free of the frustrating nature of learning to code. 
![python versus scratch](paper_images/python_scratch.png "Optional title text")
*Side by side comparison of scratch versus python*

Upon it's initial completion scratch had two defining features.
1. **Drag and Drop Blocks** Scratch is programmed through drag and drop blocks, allowing for novices to learn in a more intuitive way. As well as preventing students from copying and pasting answers, ensuring that their exploration and interaction with the material remains exploratory. 
2. **Examples** Scratch comes preloaded with examples and tutorials, leading to a more streamlined experience.    


# Summary

Data science is often taught at the upper undergraduate levels, with programming often cited as a prerequisite for learning data science. DataScratch is software intended to teach novices the core concepts of data science, without the prerequisite of knowing how to program. DataScratch achieves this via an intuitive drag and drop interface modeled after scratch.

# Statement of need

The current educational landscape presents a significant hurdle for novices seeking to engage with data science. While foundational mathematical concepts like algebra and basic statistics are often introduced in high school, students often do not study data science and AI until middle-late undergraduate. 

Many educators cite that programming is a barrier to entry to data science. This is because many tools and libraries for data science are called programmatically. The cognitive load associated with learning both programming syntax and complex statistical concepts simultaneously is often deemed detrimental to meaningful learning.

This lack of accessible entry points limits the potential for widespread data science literacy. As AI increasingly permeates various aspects of modern life understanding its underlying principles becomes essential.  Data science literacy empowers individuals to critically evaluate these systems, fostering informed decision-making and promoting responsible technological development. Moreover, a basic grasp of AI models can demystify complex technologies, enabling students to navigate a world shaped by intelligent systems with greater confidence and agency.

Therefore, there's an urgent need for tools that prioritize accessibility and intuitive learning. A low barrier to entry is paramount; users should be able to explore core data science concepts without needing prior programming experience. This necessitates a paradigm shift away from code-centric approaches towards user-friendly interfaces that abstract the complexities of programming while preserving the fundamental principles of data analysis.

DataScratch directly addresses this need by offering a visual, drag-and-drop environment for building and experimenting with AI models. By removing the immediate requirement to write code, DataScratch provides novice users with an accessible gateway to exploring core concepts in data science and AI. 

# State of the field

There are several no-code, low code platforms available on the internet. However these are often designed with power users in mind, and are often expensive, making them frustrating to novices. Many of these softwares are geared toward commercial data science use, with a focus on integration with common business tools. 

| Name        | Description                | Target Audience | License              | Drag and drop |
|-------------|----------------------------|-----------------|----------------------|---------------|
| DataBricks  | Generative AI              | Businesses     | Paid / Commercial    | No            |
| Power BI    | Visualization Interface    | Businesses     | Paid / Commercial    | Yes           |
| Rapid Miner | Training / Visualization   | Data Scientists | Free for individuals | No            |
| JASP        | Statistics / Visualization | High Undergraduate / Graduate        | Free                 | No            |

Scratch, a visual programming language designed for children, offers a compelling model for accessible computational learning. Its intuitive drag-and-drop interface allows beginners to grasp fundamental programming concepts without needing to decipher complex syntax. Scratch's interface has been proven to be effective at teaching novices programming concepts, and assist learners when the transition to "real" programming.

# Software design

The language for this software is python, this is because python possesses several libraries, such as pandas, matplotlib, and scikit-learn, which are standard tools for data science and AI modeling. Another reason would be portability. If a user desires features that are beyond the scope of DataScratch, the software is built in a way the models and utilizes underlying data science libraries, to make the transition from using DataScratch to programming in python easier.

The GUI software was originally written using a python library called PyGtk, however after several months of development this library was dropped, due to the PyGtk library having a non-functional pip installation, and graphical issues when run on windows. Additionally, electron was considered, with the benefit being easier styling, however it did not posses seamless python support. The project later switched to PyQt, which featured cross platform support, and allowed for installation via pip by default. 

The drag and drop components are modeled closely after scratch.  The shape of each draggable block corresponds to a shape on the pipeline to give the user visual signifiers telling them where things should go. The purpose of this change is to reduce the complexity of the interface.  
![blocks v python](paper_images/Python_v_datascratch.png "Image showing the complexity of coding versus the new drag and drop interface.")

The interface also enables the user to assemble and train multiple models at once, allowing for quick model comparison. This enables common user desires within data science, where data scientists often compare and contrast models. Another purpose of this feature is to allow users to learn the differences between certain models. 
![model comparison](paper_images/Example_model_comparison.svg "Image showing model comparison for the software. ")

Additionally, Datascratch comes pre-loaded with several example datasets, which have been crafted to be usable to a wide range of users, allowing novices to get learning right away, without having to procure a dataset first. The image below shows the output from a descriptive statistics query.  
![example dataset descriptive statistics](paper_images/diamonds_descriptive.png "Image showing descriptive statistics for the diamonds dataset")

The interface also allows the user to input manual predictions, allowing for novices to interact with their new models. This tab enables the user to export their saved models as software, which is where a user can save their trained model, and access it later. The software also enables the exporting as pickle, which fulfills the needs of potential power users. 
![example dataset descriptive statistics](paper_images/example_predictor.png "Image showing two predictors for the diamonds dataset")


## Running the current GUI

Works on Linux , Windows , Mac
Make a virtual environment
```
python -m venv myenv
```
Then activate your virtual environment.
```
# Linux / Mac / Git bash
source ./myenv/bin/activate

# Or

# Windows
call myenv\scripts\activate.bat
```
Install the required dependencies.
```
pip install ".[dev]"
pip install -e .
pip install requirments.txt
```
Running the GUI (This may be slow the first time you run it).
```
datascratch
```
Running Unit tests
```
pytest --cov=..
```


