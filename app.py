from flask import Flask, render_template, request, jsonify

from database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from database.events.upcoming_events import UPCOMING_EVENTS
from database.organization.affiliates import AFFILIATES
from database.tricks import PROP_TO_TRICKS
from route_generator.exceptions import NotEnoughTricksFoundException
from route_generator.prop import PROP_OPTIONS, Prop
from route_generator.route_generator import RouteGenerator
from route_generator.tricks.tags import TAG_OPTIONS, Tag

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
        return render_template('generate_route.html', current_page='generate_route', tag_options=TAG_OPTIONS, prop_options=PROP_OPTIONS)
    
    route_name = request.form['route_name']
    prop = request.form['prop']
    min_props = int(request.form['min_props'])
    max_props = int(request.form['max_props'])
    min_difficulty = int(request.form['min_difficulty'])
    max_difficulty = int(request.form['max_difficulty'])
    route_length = int(request.form['route_length'])
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
            name=route_name
        )
        return render_template('created_route.html', route=route)
    except NotEnoughTricksFoundException:
        return '<p class="no-tricks">No tricks were generated. Try adjusting your criteria.</p>'

@app.route('/host_event', methods=['GET'])
def host_event():
    return render_template('host_event.html', affiliates=AFFILIATES)

@app.route('/build_route', methods=['GET'])
def build_route():
    # Get all available props and tags
    prop_options = [prop.value for prop in Prop]
    tag_options = [tag.value for tag in Tag]
    
    # Convert PROP_TO_TRICKS to use string keys and serialize tricks
    prop_to_tricks_dict = {
        prop.value: [trick.to_dict() for trick in tricks]
        for prop, tricks in PROP_TO_TRICKS.items()
    }
    
    return render_template('build_route.html', 
                         current_page='build_route', 
                         prop_options=prop_options,
                         tag_options=tag_options,
                         prop_to_tricks=prop_to_tricks_dict)

@app.route('/api/search_tricks', methods=['GET'])
def search_tricks():
    prop = request.args.get('prop')
    search_term = request.args.get('search', '').lower()
    min_props = request.args.get('min_props', type=int)
    max_props = request.args.get('max_props', type=int)
    min_difficulty = request.args.get('min_difficulty', type=int)
    max_difficulty = request.args.get('max_difficulty', type=int)
    tags = request.args.getlist('tags')
    
    tricks = PROP_TO_TRICKS[Prop.get_key_by_value(prop)]
    
    # Filter tricks based on search criteria
    filtered_tricks = []
    for trick in tricks:
        # Name search
        if search_term and search_term not in trick.name.lower():
            continue
            
        # Prop count range
        if min_props is not None and trick.props_count < min_props:
            continue
        if max_props is not None and trick.props_count > max_props:
            continue
            
        # Difficulty range
        if min_difficulty is not None and trick.difficulty < min_difficulty:
            continue
        if max_difficulty is not None and trick.difficulty > max_difficulty:
            continue
            
        # Tag intersection
        if tags and not trick.tags:
            continue
        if tags and not any(tag in trick.tags for tag in tags):
            continue
            
        filtered_tricks.append({
            'name': trick.name,
            'props_count': trick.props_count,
            'difficulty': trick.difficulty,
            'tags': [tag.value for tag in trick.tags] if trick.tags else [],
            'comment': trick.comment
        })
    
    return jsonify(filtered_tricks)

@app.route('/api/preview_route', methods=['POST'])
def preview_route():
    route_data = request.json
    # TODO: Implement route preview using route_display.html
    return render_template('utils/route_display.html', route=route_data)

@app.route('/api/save_route', methods=['POST'])
def save_route():
    route_data = request.json
    # TODO: Implement route saving
    return jsonify({'success': True, 'route_id': '123'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)