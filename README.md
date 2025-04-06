# JuggleFit Website

Welcome to the JuggleFit website, a platform for a revolutionary sport-juggling competition inspired by CrossFit. JuggleFit aims to create a motivating, fair, and exciting competition that measures juggling skill through control over specific tricks, with minimal preparation required. This website serves as the hub for event information, route creation, and community engagement.

This repository contains the source code for the JuggleFit website, built using Flask, Python, and modern web technologies. Whether you're a juggler, event host, or developer, you’re welcome to explore, use, or contribute! The site is currently hosted on Render for public access.

You can view a live demo at [jugglefit.org](www.jugglefit.org)

## Setup

1. Ensure you have Python installed (`python --version` should return 3.9 or higher; recommended: 3.11 for compatibility with the project).
2. Install required Python packages: `pip install -r requirements.txt`. Ensure `pip` is up to date (`pip install --upgrade pip` if needed).
3. Clone or download this repository.
4. Ensure you have a web browser installed to view the site locally.
5. Navigate to the project directory in your terminal.

**Note**: This project uses Flask, Jinja2, and noUISlider for sliders. No database is required for basic functionality, but you may need to set up a virtual environment for dependency isolation (`python -m venv venv` and `source venv/bin/activate` on Unix or `venv\Scripts\activate` on Windows).

## Running the Website

1. Run the Flask application: `python app.py` or `flask run` if you’ve configured Flask correctly.
2. Open a web browser and go to `http://127.0.0.1:5000/` to view the homepage.
3. Explore additional routes:
   - Home: `http://127.0.0.1:5000/`
   - Create a Route: `http://127.0.0.1:5000/create_route`
   - Host an Event: `http://127.0.0.1:5000/host_event`
   - Past Events: `http://127.0.0.1:5000/past_events`

**Troubleshooting**:
- If you encounter a "Port already in use" error, stop any running Flask instances or use `flask run --port 5001` to use a different port.
- Ensure all static files (CSS, JS, images) are in the `static/` directory and correctly referenced in templates.

## Development and Testing

- **Current Limitations**: Form submissions (e.g., route creation, event hosting) currently print to the console for debugging. No persistent storage (e.g., database) is implemented yet, but you can extend this using Flask-SQLAlchemy or a similar ORM.
- **Testing**: Use a local Flask server (`python app.py`) to test changes. Ensure static files (CSS, JS, images) are correctly referenced and loaded.
- **Debugging**: Enable Flask’s debug mode by setting `app.debug = True` in `app.py` for detailed error messages during development.
- **Extending the Project**: To add persistent storage, update `app.py` to include a database (e.g., SQLite, PostgreSQL) and modify routes to save/load data.

## Contributing

We welcome contributions to enhance JuggleFit! Here’s how you can help:

1. **Fork the Repository**: Click the "Fork" button on GitHub to create your own copy.
2. **Clone Locally**: `git clone https://github.com/your-username/jugglefit_website.git`.
3. **Create a Branch**: Use `git checkout -b feature/your-feature-name`.
4. **Make Changes**: Update code, add features, or fix bugs. Follow the coding style in existing files (e.g., PEP 8 for Python, consistent HTML/CSS).
5. **Test Locally**: Run `python app.py` and ensure your changes work as expected.
6. **Submit a Pull Request**: Push your changes to GitHub and open a PR against the `main` branch. Include a description of your changes and any testing notes.

**Code of Conduct**: Please respect our community by adhering to the Contributor Covenant (we’ll adopt one if not already in place).

For major changes, open an issue first to discuss your proposal. Contact us at `jugglefit.competition@gmail.com` for questions or collaboration.

## Contact and Support

For questions, feedback, or collaboration, reach out to us at `jugglefit.competition@gmail.com`. You can also open an issue on GitHub for technical support or feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Notes

- The website uses a fitness-inspired color scheme (reds, blacks, whites) and is mobile-friendly.
- Form submissions currently print to the console; no persistent storage is implemented yet.