from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
from datetime import datetime

from database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from database.events.upcoming_events import UPCOMING_EVENTS
from database.organization.affiliates import AFFILIATES
from database.tricks import PROP_TO_TRICKS
from py_lib.prop import PROP_OPTIONS, Prop
from py_lib.tag import TAG_OPTIONS, Tag
from py_lib.route import Route
from py_lib.utils.general import has_intersection

from route_generator.route_generator import RouteGenerator
from route_generator.exceptions import NotEnoughTricksFoundException

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', upcoming_events=UPCOMING_EVENTS, last_events=FRONT_PAGE_PAST_EVENTS)


@app.route('/past_events', methods=['GET'])
def past_events():
    return render_template('past_events.html', past_events=ALL_PAST_EVENTS)


@app.route('/generate_route', methods=['GET', 'POST'])
def generate_route():
    if request.method == 'GET':
        return render_template('generate_route.html', 
                             current_page='generate_route', 
                             tag_options=TAG_OPTIONS, 
                             prop_options=PROP_OPTIONS)
    
    route_name = request.form['route_name']
    prop = request.form['prop']
    min_props = int(request.form['min_props'])
    max_props = int(request.form['max_props'])
    min_difficulty = int(request.form['min_difficulty'])
    max_difficulty = int(request.form['max_difficulty'])
    route_length = int(request.form['route_length'])
    route_duration_seconds = int(request.form['route_duration']) * 60  # Convert minutes to seconds
    exclude_tags = {Tag.get_key_by_value(key) for key in request.form.getlist('exclude_tags')}
    
    try:
        route = RouteGenerator.generate(
            prop=Prop.get_key_by_value(prop),
            min_props=min_props,
            max_props=max_props,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty,
            route_length=route_length,
            exclude_tags=exclude_tags,
            name=route_name,
            duration_seconds=route_duration_seconds
        )
        # Serialize the route and redirect to created_route with POST data
        serialized = route.serialize()
        return redirect(url_for('created_route', route=serialized))
    except NotEnoughTricksFoundException:
        return '<p class="no-tricks">No tricks were generated. Try adjusting your criteria.</p>'

@app.route('/host_event', methods=['GET'])
def host_event():
    return render_template('host_event.html', affiliates=AFFILIATES)

@app.route('/build_route')
def build_route():
    # Get the serialized route from query params if it exists
    serialized_route = request.args.get('route')
    initial_route = None
    if serialized_route:
        try:
            initial_route = Route.deserialize(serialized_route)
        except:
            # If there's any error in decoding, ignore the parameter
            pass

    # Get available props and tags
    available_props = [prop.value for prop in Prop]  # Convert Prop enum to string values
    available_tags = list(TAG_OPTIONS)

    # Create a dictionary mapping each prop to its list of tricks
    prop_to_tricks_dict = {}
    for prop, tricks in PROP_TO_TRICKS.items():
        prop_to_tricks_dict[prop.value] = [trick.to_dict() for trick in tricks]  # Use prop.value instead of prop

    # Convert initial_route to dict if it exists
    initial_route_dict = initial_route.to_dict() if initial_route else None

    return render_template('build_route.html',
                         prop_options=available_props,
                         tag_options=available_tags,
                         prop_to_tricks=prop_to_tricks_dict,
                         default_max_props=9,
                         initial_route=initial_route_dict)

@app.route('/api/serialize_route', methods=['POST'])
def serialize_route():
    route_data = request.json
    try:
        # Log the received data for debugging
        print("Received route data:", route_data)
        
        # Create a Route instance from the JSON data
        route = Route.from_dict(route_data)
        
        # Log the created route for debugging
        print("Created route:", route)
        
        # Serialize using the Route class method
        serialized = route.serialize()
        print("Serialized route:", serialized)
        
        return serialized
    except Exception as e:
        print("Error serializing route:", str(e))
        return str(e), 400

@app.route('/created_route', methods=['GET', 'POST'])
def created_route():
    # Try to get route from either GET or POST parameters
    route_param = request.args.get('route') or request.form.get('route')
    if not route_param:
        return redirect(url_for('build_route'))
    
    try:
        route = Route.deserialize(route_param)
        return render_template('created_route.html', route=route)
    except Exception as e:
        flash(f'Error loading route: {str(e)}')
        return redirect(url_for('build_route'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)