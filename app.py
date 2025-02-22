from flask import Flask, render_template, request
import random


from static.siteswaps import generate_random_tricks



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


@app.route('/create_path', methods=['GET', 'POST'])
def create_path():
    if request.method == 'POST':
        workout_name = request.form['workout_name']
        min_props = int(request.form['min_props'])
        max_props = int(request.form['max_props'])
        max_height = int(request.form['max_height'])
        include_tricks = request.form.getlist('include_tricks')
        exclude_tricks = request.form.getlist('exclude_tricks')

        # Print form data to console (placeholder for backend logic)
        print(f"{workout_name = }")
        print(f"{max_props = }")
        print(f"{max_props = }")
        print(f"{max_height = }")
        print(f"{include_tricks = }")
        print(f"{exclude_tricks = }")


        props_list = [(i, random.randint(min_props, max_props + 1)) for i in range(3, max_props + 1)]

        tricks = generate_random_tricks(props_list, include_tricks=include_tricks, exclude_tricks=exclude_tricks)

        return render_template('tricks_display.html', tricks=tricks, workout_name=workout_name)
    return render_template('create_path.html', current_page='create_path')


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