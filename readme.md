![blocks v python](resources/Full_logo_SciKit_Grow.svg "Optional title text")

## Background & Inspiration

Invented in 2003 scratch is a programming language intended for children ages 10 - 15. The intent of this project was to model programming concepts via large colorful blocks, to teach children the basics of programming. Scratch has since been a massive success, as of 2023 scratch go 95 million monthly visits, some fo those recurring users, other programming novices. 

This language was intended to model real world programming, whilst giving children a streamlined experience, free of the frustrating nature of learning to code. 
![python versus scratch](paper_images/python_scratch.png "Optional title text")
*Side by side comparison of scratch versus python*

Upon it's initial completion scratch had three defining features.
1. **The scratch compiler ALWAYS compiles** Scratch will never throw an exception or raise a ValueError, this was to shield novices from the frustration of syntax errors.
2. **Drag and Drop Blocks** Scratch is programmed through drag and drop blocks, allowing for novices to learn in a more intuitive way. As well as preventing students from copying and pasting answers, ensuring that their exploration and interaction with the material remains exploratory. 
3. **Examples** Scratch comes preloaded with examples and tutorials, leading to a more streamlined experience.    

##  Project Goals & Summary
The goal of this project is to make a learning software for novices and high schoolers to learn core data science concepts, such as overfiting, and linear vs non-linear models. 

The goal of this project is to build a drag and drop interface, similar to scratch, where users can drag and drop parts of a data science pipeline to make charts, export models, and save.
![blocks v python](paper_images/blocks_vs_python.png "Optional title text")
*A draft of the current drag and drop interface versus python code.*



### Project sub-goals:
1. **Project always compiles** DataSeedlings should never not compile, the compiler should be written in a way that the project always results in an output, even if that output is a blank graph. 
2. **Drag and drop data-science components** Drag and drop column values, as well as sklearn components to build and AI model. 
3. **Examples** This software should have example datasets, and later linked tutorials to facilitate learning. 
4. **Compatibility** This software should allow for the exporting and saving of data, so students can save their projects and share them (presumably with proud parents)

## Exploratory Learning
This project is supposed to encourage exploration and experimentation. The modular drag and drop system is part of this, allowing for users to swap out models on the fly, leading to them learning the differences between different models more in-depth, due to a tactile, hands on experience.

## Current progress
Currently, there is still a lot to work on for this application, most of the core application features have been implemented, but there is still a lot of software development left to do. 

![blocks v python](paper_images/overall_proccess.svg "Optional title text")


## Running the current GUI

Works on Linux , Windows , Mac
```
python -m venv myenv
echo "Then activate your venv, this varies slightly from platform to platform. The below command is for Unix-like systems. It is different for Mac and Powershell."
source ./myenv/bin/activate
pip install -r requirments.txt
```
Running the GUI
```
python main.py
```



