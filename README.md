Welcome to the JuggleFit website, a platform for a revolutionary sport-juggling competition. JuggleFit aims to create a motivating, fair, and exciting competition that measures juggling skill through control over specific tricks, with minimal preparation required. This website serves as the hub for event information, route creation, and community engagement.

This repository contains the source code for the JuggleFit website, built using Flask, Python, and modern web technologies. Whether you're a juggler, event host, or developer, you're welcome to explore, use, or contribute! The site is currently hosted on Render for public access.

You can view a live demo at [jugglefit.org](www.jugglefit.org)

# JuggleFit Website

A website for juggling tricks and training.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with:
```
# Google Sheets API Configuration
JUGGLEFIT_BOT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----"
TRICK_SUGGESTIONS_SPREADSHEET_ID=your_spreadsheet_id
```

3. Run the development server:
```bash
flask run
```

## Environment Variables

- `JUGGLEFIT_BOT_PRIVATE_KEY`: Service account private key for Google Sheets API
- `TRICK_SUGGESTIONS_SPREADSHEET_ID`: ID of the Google Sheet for trick suggestions 

## Contribution
We manage the development in a ClickUp.
If you are up to join the development, reach us by Email at jugglefit.competition@gmail.com
