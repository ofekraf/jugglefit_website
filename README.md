# JuggleFit Website

This is a website for JuggleFit, a new sport juggling competition inspired by CrossFit.

## Setup

1. Ensure you have Python installed (`python --version` should return 3.x).
2. Install requirements: `pip install -r requirements.txt`.
3. Clone or download this repository.
5. Navigate to the project directory in your terminal.

## Running the Website

1. Run the Flask application: `python app.py`.
2. Open a web browser and go to `http://127.0.0.1:5000/` to view the website.

## File Structure

- `app.py`: Flask application with routes and form handling.
- `templates/`: HTML templates for each page.
- `static/css/`: CSS files for styling.
- `static/images/`: Image assets (e.g., `jugglefit_logo.png`).

## Notes

- The website uses a fitness-inspired color scheme (reds, blacks, whites) and is mobile-friendly.
- Form submissions currently print to the console; no persistent storage is implemented yet.
