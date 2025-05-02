from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Blueprint
from database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from database.events.upcoming_events import UPCOMING_EVENTS
from database.organization.affiliates import AFFILIATES
from py_lib.prop import Prop
from py_lib.tag import Tag, TagCategory
from py_lib.route import Route
from py_lib.consts import (
    MIN_TRICK_PROPS_COUNT, MAX_TRICK_PROPS_COUNT,
    MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY,
    DEFAULT_MIN_TRICK_PROPS_COUNT, DEFAULT_MAX_TRICK_PROPS_COUNT,
    DEFAULT_MIN_TRICK_DIFFICULTY, DEFAULT_MAX_TRICK_DIFFICULTY
)
from py_lib.utils.filter_tricks import filter_tricks
from route_generator.route_generator import RouteGenerator
from route_generator.exceptions import NotEnoughTricksFoundException

app = Flask(__name__)

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/serialize_route', methods=['POST'])
def serialize_route():
    route_data = request.json
    try:
        route = Route.from_dict(route_data)
        serialized = route.serialize()
        return serialized
    except Exception as e:
        return str(e), 400

@api.route('/get_tricks', methods=['POST'])
def get_tricks():
    try:
        data = request.get_json()
        prop_type = Prop.get_key_by_value(data.get('prop_type'))
        min_props = int(data.get('min_props', MIN_TRICK_PROPS_COUNT))
        max_props = int(data.get('max_props', MAX_TRICK_PROPS_COUNT))
        min_difficulty = int(data.get('min_difficulty', MIN_TRICK_DIFFICULTY))
        max_difficulty = int(data.get('max_difficulty', MAX_TRICK_DIFFICULTY))
        exclude_tags = data.get('exclude_tags', [])
        limit = int(data.get('limit', 0))

        exclude_tags_set = {Tag.get_key_by_value(tag) for tag in exclude_tags}

        filtered_tricks = filter_tricks(
            prop=prop_type,
            min_props=min_props,
            max_props=max_props,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty,
            limit=limit if limit > 0 else None,
            exclude_tags=exclude_tags_set
        )

        tricks_dict = [trick.to_dict() for trick in filtered_tricks]
        return jsonify(tricks_dict)
    except Exception as e:
        return str(e), 400

# Register the API blueprint
app.register_blueprint(api)

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
                             tag_options=list(Tag),
                             tag_categories=list(TagCategory),
                             prop_options=list(Prop))
    
    route_name = request.form['route_name']
    prop = request.form['prop']
    min_props = int(request.form['min_props'])
    max_props = int(request.form['max_props'])
    min_difficulty = int(request.form['min_difficulty'])
    max_difficulty = int(request.form['max_difficulty'])
    route_length = int(request.form['route_length'])
    route_duration_seconds = int(request.form['route_duration']) * 60
    exclude_tags = {Tag.get_key_by_value(tag) for tag in request.form.getlist('exclude_tags') if Tag.get_key_by_value(tag) is not None}
    
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
        serialized = route.serialize()
        return redirect(url_for('created_route', route=serialized))
    except NotEnoughTricksFoundException:
        return '<p class="no-tricks">No tricks were generated. Try adjusting your criteria.</p>'

@app.route('/host_event', methods=['GET'])
def host_event():
    return render_template('host_event.html', affiliates=AFFILIATES)

@app.route('/build_route')
def build_route():
    route_param = request.args.get('route')
    initial_route = None
    if route_param:
        try:
            route = Route.deserialize(route_param)
            initial_route = {
                'name': route.name,
                'prop': route.prop.value,
                'duration_seconds': route.duration_seconds,
                'tricks': [{
            'name': trick.name,
            'props_count': trick.props_count,
            'difficulty': trick.difficulty,
                    'tags': [tag.value for tag in trick.tags] if trick.tags else None,
            'comment': trick.comment
                } for trick in route.tricks]
            }
        except Exception as e:
            flash(f'Error loading route: {str(e)}', 'error')
            return redirect(url_for('build_route'))

    return render_template('build_route.html',
                         prop_options=list(Prop),
                         tag_options=list(Tag),
                         tag_categories=list(TagCategory),
                         initial_route=initial_route,
                         MIN_TRICK_PROPS_COUNT=MIN_TRICK_PROPS_COUNT,
                         MAX_TRICK_PROPS_COUNT=MAX_TRICK_PROPS_COUNT,
                         MIN_TRICK_DIFFICULTY=MIN_TRICK_DIFFICULTY,
                         MAX_TRICK_DIFFICULTY=MAX_TRICK_DIFFICULTY,
                         DEFAULT_MIN_TRICK_PROPS_COUNT=DEFAULT_MIN_TRICK_PROPS_COUNT,
                         DEFAULT_MAX_TRICK_PROPS_COUNT=DEFAULT_MAX_TRICK_PROPS_COUNT,
                         DEFAULT_MIN_TRICK_DIFFICULTY=DEFAULT_MIN_TRICK_DIFFICULTY,
                         DEFAULT_MAX_TRICK_DIFFICULTY=DEFAULT_MAX_TRICK_DIFFICULTY)

@app.route('/created_route', methods=['GET', 'POST'])
def created_route():
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