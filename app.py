from urllib.parse import unquote
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Blueprint
from database.memory_url_shortener import get_long_url_and_refresh, get_or_create_short_url, init_db, start_cleanup_thread
from hardcoded_database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from hardcoded_database.events.upcoming_events import UPCOMING_EVENTS
from hardcoded_database.organization.team import TEAM

from dotenv import load_dotenv

from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.tag import TAG_CATEGORY_MAP, Tag, TagCategory
from pylib.configuration.consts import DEFAULT_MAX_TRICK_DIFFICULTY, DEFAULT_MAX_TRICK_PROPS_COUNT, DEFAULT_MIN_TRICK_DIFFICULTY, DEFAULT_MIN_TRICK_PROPS_COUNT, MAX_TRICK_DIFFICULTY, MAX_TRICK_PROPS_COUNT, MIN_TRICK_DIFFICULTY, MIN_TRICK_PROPS_COUNT
from pylib.route_generator.exceptions import NotEnoughTricksFoundException
from pylib.route_generator.route_generator import RouteGenerator
from pylib.utils.filter_tricks import filter_tricks

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Call init_db and start cleanup thread on app startup
with app.app_context():
    init_db()
    start_cleanup_thread()

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

@api.route('/fetch_tricks', methods=['POST'])
def fetch_tricks():
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
    
@api.route('/suggest_trick', methods=['POST'])
def api_suggest_trick():
    return "currently unsupported, in the process of building"
    # try:
    #     data = request.get_json()
    #
    #     # Validate required fields
    #     required_fields = ['name', 'prop', 'props_count', 'difficulty']
    #     for field in required_fields:
    #         if field not in data:
    #             return f'Missing required field: {field}', 400
    #
    #     prop = Prop.get_key_by_value(data.get("prop"))
    #     trick_suggestion = Trick.from_dict(data=data)
    #
    #     # Append to Google Sheet
    #     append_trick_suggestion(prop=prop, trick=trick_suggestion)
    #     return 'Suggestion submitted successfully', 200
    #
    # except Exception as e:
    #     return str(e), 400


@api.route('/shorten_url', methods=['POST'])
def shorten_url():
    long_url = request.json.get('long_url')
    if not long_url:
        return jsonify({"error": "long_url is required"}), 400
    try:
        code = get_or_create_short_url(long_url)
        short_url = url_for('redirect_to_long_url', code=code, _external=True)
        return jsonify({"short_url": short_url, "code": code}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/shortener/<code>')
def redirect_to_long_url(code):
    try:
        long_url = get_long_url_and_refresh(code)
        if long_url:
            return redirect(long_url)
        else:
            flash('Short URL not found.', 'error')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error retrieving URL: {str(e)}', 'error')
        return redirect(url_for('home'))


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
                             tag_category_map=TAG_CATEGORY_MAP,
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
    return render_template('host_event.html', team=TEAM)

@app.route('/equipment_list', methods=['GET'])
def equipment_list():
    return render_template('equipment_list.html')

@app.route('/build_route')
def build_route():
    route_param = request.args.get('route', type=str)
    initial_route = None
    if route_param:
        try:
            route = Route.deserialize(unquote(route_param))
            initial_route = route.to_dict()  # Convert to dict before passing to template
        except Exception as e:
            flash(f'Error loading route: {str(e)}', 'error')
            return redirect(url_for('build_route'))
    
    return render_template('build_route.html', 
                         prop_options=list(Prop),
                         tag_options=list(Tag),
                         tag_categories=list(TagCategory),
                         tag_category_map=TAG_CATEGORY_MAP,
                         initial_route=initial_route,
                         MIN_TRICK_PROPS_COUNT=MIN_TRICK_PROPS_COUNT,
                         MAX_TRICK_PROPS_COUNT=MAX_TRICK_PROPS_COUNT,
                         MIN_TRICK_DIFFICULTY=MIN_TRICK_DIFFICULTY,
                         MAX_TRICK_DIFFICULTY=MAX_TRICK_DIFFICULTY,
                         DEFAULT_MIN_TRICK_PROPS_COUNT=DEFAULT_MIN_TRICK_PROPS_COUNT,
                         DEFAULT_MAX_TRICK_PROPS_COUNT=DEFAULT_MAX_TRICK_PROPS_COUNT,
                         DEFAULT_MIN_TRICK_DIFFICULTY=DEFAULT_MIN_TRICK_DIFFICULTY,
                         DEFAULT_MAX_TRICK_DIFFICULTY=DEFAULT_MAX_TRICK_DIFFICULTY)

@app.route('/created_route', methods=['GET'])
def created_route():
    route_param = request.args.get('route', type=str)
    if not route_param:
        return redirect(url_for('build_route'))
    
    try:
        route = Route.deserialize(route_param)
        return render_template('created_route.html', route=route)
    except Exception as e:
        flash(f'Error loading route: {str(e)}')
        return redirect(url_for('build_route'))

@app.route('/live_event', methods=['GET'])
def live_event():
    route_param = request.args.get('route', type=str)
    if not route_param:
        return redirect(url_for('build_route'))
    
    try:
        route = Route.deserialize(route_param)
        return render_template('live_event.html', route=route)
    except Exception as e:
        flash(f'Error loading route: {str(e)}')
        return redirect(url_for('build_route'))

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/suggest_trick', methods=['GET'])
def suggest_trick():
    return render_template('suggest_trick.html',
                         prop_options=list(Prop),
                         tag_options=list(Tag),
                         tag_categories=list(TagCategory),
                         tag_category_map=TAG_CATEGORY_MAP,
                         MIN_TRICK_PROPS_COUNT=MIN_TRICK_PROPS_COUNT,
                         MAX_TRICK_PROPS_COUNT=MAX_TRICK_PROPS_COUNT,
                         MIN_TRICK_DIFFICULTY=MIN_TRICK_DIFFICULTY,
                         MAX_TRICK_DIFFICULTY=MAX_TRICK_DIFFICULTY,
                         DEFAULT_MIN_TRICK_PROPS_COUNT=DEFAULT_MIN_TRICK_PROPS_COUNT,
                         DEFAULT_MAX_TRICK_PROPS_COUNT=DEFAULT_MAX_TRICK_PROPS_COUNT,
                         DEFAULT_MIN_TRICK_DIFFICULTY=DEFAULT_MIN_TRICK_DIFFICULTY,
                         DEFAULT_MAX_TRICK_DIFFICULTY=DEFAULT_MAX_TRICK_DIFFICULTY)

@app.route('/contribute/software')
def software_contribution():
    return render_template('software_contribution.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)