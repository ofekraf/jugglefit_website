from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html', current_page='home')


@app.route('/about')
def about():
    return render_template('about.html', current_page='about')


@app.route('/rules')
def rules():
    return render_template('rules.html', current_page='rules')


@app.route('/create_path', methods=['GET', 'POST'])
def create_path():
    if request.method == 'POST':
        workout_name = request.form['workout_name']
        max_props = request.form['max_props']
        max_height = request.form['max_height']
        include_tricks = request.form.getlist('include_tricks')
        exclude_tricks = request.form.getlist('exclude_tricks')

        # Print form data to console (placeholder for backend logic)
        print(f"Workout Name: {workout_name}")
        print(f"Max Props: {max_props}")
        print(f"Max Height: {max_height}")
        print(f"Include Tricks: {include_tricks}")
        print(f"Exclude Tricks: {exclude_tricks}")

        return "Routine created successfully!"  # Temporary response
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
