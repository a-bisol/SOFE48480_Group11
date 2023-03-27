# PyHide

`PiHide` allows users to quickly encode and decode hidden messages into images using various optional encryption algorithms.

# Table of Contents
  * [Requirements](#requirements)
  * [Installation and Usage](#Installation-and-Usage)
  * [Potential improvements](#potential-improvements)
# Requirements

 - Python 3.x with the following packages:
	 - Pillow~=9.4.0
	 - pycryptodome~=3.17

# Installation and Usage

Installation is as simple as installing the packages within [requirements.txt](requirements.txt) using pip or your preferred package manager.

Execute [PyHide.py](steganographImage/PyHide.py) and follow the onscreen prompts.
Ensure all relevant text/image/JSON files are contained within the same folder as PyHide.py

# Potential Improvements

 - Clean up user interface using either:
	 - GUI program
	 - Website/web server
 - Allow usage of more than .png or .bmp files
 - Select which channel will be modified
 - Batch processing of multiple images/files at once
