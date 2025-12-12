import os
import string
import random
from urllib.parse import unquote
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Blueprint, send_file
from hardcoded_database.consts import get_trick_csv_path, URL_RETENTION_MONTHS
from hardcoded_database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from hardcoded_database.events.upcoming_events import UPCOMING_EVENTS
from hardcoded_database.organization.team import TEAM

from dotenv import load_dotenv

from database.db_manager import db_manager
from pylib.classes.prop import MAIN_PROPS, Prop
from pylib.classes.route import Route
from pylib.classes.tag import TAG_CATEGORY_MAP_JSON, Tag, TagCategory
from hardcoded_database.tricks import ALL_PROPS_SETTINGS, ALL_PROPS_SETTINGS_JSON
from pylib.route_generator.exceptions import NotEnoughTricksFoundException
from pylib.route_generator.route_generator import RouteGenerator
from pylib.utils.filter_tricks import filter_tricks
from pylib.configuration.consts import (
	MIN_TRICK_DIFFICULTY,
	MAX_TRICK_DIFFICULTY,
)

# Load environment variables
load_dotenv()


app = Flask(__name__)
# Note: siteswap formatting is now handled client-side in static/js/siteswap_x.js

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/fetch_tricks', methods=['POST'])
def fetch_tricks():
	try:
		data = request.get_json()
		prop_type_value = data.get('prop_type')
		try:
			prop_type = Prop.get_key_by_value(prop_type_value)
		except Exception as e:
			allowed = [v.value for v in Prop]
			msg = f"Invalid prop_type '{prop_type_value}'. Allowed values: {allowed}"
			print(msg)
			return jsonify({'error': msg}), 400
		min_props = int(data.get('min_props', ALL_PROPS_SETTINGS[prop_type].min_props))
		max_props = int(data.get('max_props', ALL_PROPS_SETTINGS[prop_type].max_props))
		min_difficulty = int(data.get('min_difficulty', MIN_TRICK_DIFFICULTY))
		max_difficulty = int(data.get('max_difficulty', MAX_TRICK_DIFFICULTY))
		exclude_tags = data.get('exclude_tags', [])
		limit = int(data.get('limit', 0))
		max_throw = int(data.get('max_throw')) if data.get('max_throw') is not None else None

		exclude_tags_set = {Tag.get_key_by_value(tag) for tag in exclude_tags}

		filtered_tricks = filter_tricks(
			prop=prop_type,
			min_props=min_props,
			max_props=max_props,
			min_difficulty=min_difficulty,
			max_difficulty=max_difficulty,
			limit=limit if limit > 0 else None,
			exclude_tags=exclude_tags_set,
			max_throw=max_throw,
		)

		tricks_dict = [trick.to_dict() for trick in filtered_tricks]
		return jsonify(tricks_dict)
	except Exception as e:
		import traceback
		print('Error in /api/fetch_tricks:', e)
		traceback.print_exc()
		return jsonify({'error': str(e)}), 400
	

@api.route('/shorten_url', methods=['POST'])
def shorten_url():
	long_url = request.json.get('long_url')
	if not long_url:
		return jsonify({"error": "long_url is required"}), 400
	
	try:
		# Check if URL already exists
		existing_code = db_manager.get_short_code_by_long_url(long_url)
		if existing_code:
			short_url = url_for('redirect_to_long_url', code=existing_code, _external=True)
			return jsonify({"short_url": short_url, "code": existing_code}), 200

		# Generate a random short code
		chars = string.ascii_letters + string.digits
		max_retries = 5
		for _ in range(max_retries):
			code = ''.join(random.choice(chars) for _ in range(8))
			# Save to database
			if db_manager.create_short_url(code, long_url):
				short_url = url_for('redirect_to_long_url', code=code, _external=True)
				return jsonify({"short_url": short_url, "code": code}), 200
		
		return jsonify({"error": "Failed to create unique short URL"}), 500
			
	except Exception as e:
		return jsonify({"error": "Database unavailable"}), 503
	
@app.route('/shortener/<code>')
def redirect_to_long_url(code):
	try:
		long_url = db_manager.get_long_url(code)
		if long_url:
			return redirect(long_url)
		else:
			flash('Short URL not found.', 'error')
			return redirect(url_for('home'))
	except Exception as e:
		flash('Service temporarily unavailable. Please try again later.', 'error')
		return redirect(url_for('home'))


# Register the API blueprint
app.register_blueprint(api)

@app.route('/health')
def health_check():
	"""Health check endpoint for container health checks."""
	return {'status': 'healthy', 'message': 'Application is running'}, 200

@app.route('/ready')
def readiness_check():
	"""Readiness check endpoint for load balancers."""
	return {'status': 'ready', 'message': 'Application is ready to serve requests'}, 200

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
					 tag_category_map=TAG_CATEGORY_MAP_JSON,
					 tag_categories=list(TagCategory),
						props_settings=ALL_PROPS_SETTINGS_JSON,
						main_props=MAIN_PROPS)
	
	route_name = request.form['route_name']
	prop = request.form['prop']
	min_props = int(request.form['min_props'])
	max_props = int(request.form['max_props'])
	min_difficulty = int(request.form['min_difficulty'])
	max_difficulty = int(request.form['max_difficulty'])
	route_length = int(request.form['route_length'])
	route_duration_seconds = int(request.form['route_duration']) * 60
	max_throw_str = request.form.get('max_throw', '').strip()
	max_throw = int(max_throw_str) if max_throw_str != '' else None
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
			duration_seconds=route_duration_seconds,
			max_throw=max_throw,
		)
		serialized = route.serialize()
		return redirect(url_for('created_route', route=serialized))
	except NotEnoughTricksFoundException:
		return '<p class="no-tricks">Not enough tricks in database. Try adjusting your criteria.</p>'

@app.route('/host_event', methods=['GET'])
def host_event():
	return render_template('host_event.html', team=TEAM)

@app.route('/event_checklist', methods=['GET'])
def equipment_list():
	return render_template('event_checklist.html')

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
			 tag_category_map=TAG_CATEGORY_MAP_JSON,
			 tag_categories=list(TagCategory),
				props_settings=ALL_PROPS_SETTINGS_JSON,
				initial_route=initial_route,
				main_props=[Prop.Balls.value, Prop.Clubs.value, Prop.Rings.value])

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


@app.route('/contribute/software')
def software_contribution():
	return render_template('software_contribution.html')

@app.route('/contribute/expand_database')
def expand_database():
	return render_template('expand_database.html', 
						 prop_options=list(Prop))

@app.route('/contribute/download_tricks_csv/<prop_type>')
def download_tricks_csv(prop_type):
	try:
		csv_path = get_trick_csv_path(Prop.get_key_by_value(prop_type))
		
		if not csv_path.exists():
			return f"CSV file for {prop_type} not found", 404
		
		return send_file(
			csv_path,
			mimetype='text/csv',
			as_attachment=True,
			download_name=f'{prop_type}_tricks.csv'
		)
		
	except Exception as e:
		return f"Error serving CSV: {str(e)}", 500

@app.route('/siteswap_x')
def siteswap_x():
		  return render_template('siteswap_x.html')

if __name__ == '__main__':
	# Initialize database
	try:
		db_manager.init_db()
		# Clean up inactive URLs on startup
		db_manager.delete_inactive_urls(URL_RETENTION_MONTHS)
	except Exception as e:
		print(f"Warning: Database initialization/migration failed: {e}")

	port = int(os.environ.get("PORT", 5001))
	app.run(host='0.0.0.0', port=port, debug=True)
