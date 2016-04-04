#C3.py

Commit Counter Chart is a Python Flask app to view git history using D3.js

![](screencast.gif)

The name is a play on D3.js. I wanted to play around with Flask and D3, and ended up visualizing git history as a form of a [live git log](https://gist.github.com/kdheepak89/411faf89190856c6458b)

# Contributions 

I highly welcome contributions. I would like to learn how to use d3.js / flask better.

# Installation

    pip install -r requirements.txt
    
You also need to install `graphviz-dev`.

# Running

Run `python app.py` to start the application. 

Open `http://localhost:5000` to view the live git log of the current repo. You can enter the path to other repos in the text field.

This application is meant for use only on a local machine
