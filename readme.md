![blocks v python](48x48/apps/Full_logo_SciKit_Grow.svg "Optional title text")

## Background & Inspiration

Invented in 2003 scratch is a programming language intended for children ages 10 - 15. The intent of this project was to model programming concepts via large colorful blocks, to teach children the basics of programming. Scratch has since been a massive success, as of 2023 scratch go 95 million monthly visits, some fo those recurring users, other programming novices. 

This language was intended to model real world programming, whilst giving children a streamlined experience, free of the frustrating nature of learning to code. 
![python versus scratch](images/python_scratch.png "Optional title text")
*Side by side comparison of scratch versus python*

Upon it's initial completion scratch had three defining features.
1. **The scratch compiler ALWAYS compiles** Scratch will never throw an exception or raise a ValueError, this was to shield novices from the frustration of syntax errors.
2. **Drag and Drop Blocks** Scratch is programmed through drag and drop blocks, allowing for novices to learn in a more intuitive way. As well as preventing students from copying and pasting answers, ensuring that their exploration and interaction with the material remains exploratory. 
3. **Examples** Scratch comes preloaded with examples and tutorials, leading to a more streamlined experience.    

##  Project Goals & Summary
The goal of this project is to make a learning software for novices and high schoolers to learn core data science concepts, such as overfiting, and linear vs non-linear models. 

I plan to do so using a "Drag and Drop" system, very similar to how scratch operates.
![blocks v python](images/blocks_vs_python.png "Optional title text")
*A draft of the current drag and drop interface versus python code.*

This would allow students and novices to learn in a similar way to scratch, dragging and dropping components, in an intuitive manner. 

### Project sub-goals:
1. **Project always compiles** DataSeedlings should never not compile, the compiler should be written in a way that the project always results in an output, even if that output is a blank graph. 
2. **Drag and drop data-science components** Drag and drop column values, as well as sklearn components to build and AI model. 
3. **Examples** This software should have example datasets, and later linked tutorials to facilitate learning. 
4. **Compatibility** This software should allow for the exporting and saving of data, so students can save their projects and share them (presumably with proud parents)

## Exploratory Learning
This project is supposed to encourage exploration and experimentation. The modular drag and drop system is part of this, allowing for users to swap out models on the fly, leading to them learning the differences between different models more in-depth, due to a tactile, hands on experience.

## Current progress
Currently, there is still a lot to work on for this application, most of the core application features have been implemented, but there is still a lot of software development left to do. 

![blocks v python](images/overall_proccess.svg "Optional title text")


## Running the current GUI
Warning; this is a work in progress, and bugs are a near guarantee. This has been tested on Linux, and nothing else. 
To install dependencies
```
./install.sh
```

To run the GUI
```
./run.sh
```
There are several other example csv's I have included, They are viewable thru the "example_datasets" folder. 


