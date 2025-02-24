from flask import Flask, render_template, request
import random


from route_generator.exceptions import NotEnoughTricksFoundException
from route_generator.prop import PROP_OPTIONS, Prop
from route_generator.route_generator import generate_route
from route_generator.tricks.tags import TAG_OPTIONS, Tag



app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html', current_page='home')


@app.route('/about')
def about():
    return render_template('about.html', current_page='about', sub_page=None)


@app.route('/about/rules')
def rules():
    return render_template('about.html', current_page='about', sub_page='rules')


@app.route('/about/previous_competitions')
def previous_competitions():
    return render_template('about.html', current_page='about', sub_page='previous_competitions')


@app.route('/create_route', methods=['GET', 'POST'])
def create_route():
    if request.method == 'POST':
        route_name = request.form['route_name']
        prop = request.form['prop']
        min_props = int(request.form['min_props'])
        max_props = int(request.form['max_props'])
        min_difficulty = int(request.form['min_difficulty'])
        max_difficulty = int(request.form['max_difficulty'])
        route_length = int(request.form['route_length'])
        exclude_tags = {Tag.get_key_by_value(key) for key in request.form.getlist('exclude_tags')}
        
        try:
            route = generate_route(
                prop=Prop.get_key_by_value(prop),
                min_props=min_props,
                max_props=max_props,
                min_difficulty=min_difficulty,
                max_difficulty=max_difficulty,
                route_length=route_length,
                exclude_tags=exclude_tags,
            )
        except NotEnoughTricksFoundException:
            route = {}  # Handled in route_display.html
        return render_template('route_display.html', route=route, prop=prop, route_name=route_name)
    return render_template('create_route.html', current_page='create_route', tag_options=TAG_OPTIONS, prop_options=PROP_OPTIONS)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Print form data to console (placeholder for backend logic)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")

        return "Message sent successfully!"  # Temporary response
    return render_template('contact.html', current_page='contact')


if __name__ == '__main__':
    app.run(debug=True)