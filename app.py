import logging
import os
import secrets
import uuid
import random
from urllib.parse import unquote
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Blueprint, send_file, session, Response, stream_with_context
from werkzeug.security import check_password_hash
from functools import wraps
from hardcoded_database.consts import get_trick_csv_path, URL_RETENTION_MONTHS
from hardcoded_database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from hardcoded_database.events.upcoming_events import UPCOMING_EVENTS
from hardcoded_database.organization.team import TEAM
from hardcoded_database.captcha import CAPTCHA_QUESTIONS
from database.db_manager import db_manager

from dotenv import load_dotenv

from pylib.classes.prop import MAIN_PROPS, Prop
from pylib.classes.route import Route
from pylib.classes.tag import TAG_CATEGORY_MAP_JSON, Tag, TagCategory
from hardcoded_database.tricks import ALL_PROPS_SETTINGS, ALL_PROPS_SETTINGS_JSON
from pylib.route_generator.exceptions import NotEnoughTricksFoundException
from pylib.route_generator.route_generator import RouteGenerator
from pylib.utils.filter_tricks import filter_tricks
from pylib.utils.verification_tricks import select_obvious_pair, select_random_pair, randomize_order
from pylib.utils.verification_logger import log_verification_result
from pylib.utils.general import add_line_breaks_to_trick_name
from pylib.configuration.consts import (
	MIN_TRICK_DIFFICULTY,
	MAX_TRICK_DIFFICULTY,
)

# Load environment variables
load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_jugglefit') # Should be set in .env for prod
# Note: siteswap formatting is now handled client-side in static/js/siteswap_x.js

# Register custom Jinja2 filter for adding line breaks to trick names
app.jinja_env.filters['add_line_breaks'] = add_line_breaks_to_trick_name

# Configure session for verification game
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

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
			app.logger.error(msg)
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
		app.logger.exception('Error in /api/fetch_tricks: %s', e)
		return jsonify({'error': str(e)}), 400
	

@api.route('/get_captcha', methods=['GET'])
def get_captcha():
	try:
		question_index = random.randint(0, len(CAPTCHA_QUESTIONS) - 1)
		question_data = CAPTCHA_QUESTIONS[question_index]
		session['captcha_index'] = question_index
		return jsonify({'question': question_data['question']})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@api.route('/suggest_trick', methods=['POST'])
def suggest_trick():
	try:
		data = request.get_json()
		prop_type = data.get('prop_type')
		name = data.get('name')
		siteswap_x = data.get('siteswap_x')
		props_count = data.get('props_count')
		difficulty = data.get('difficulty')
		max_throw = data.get('max_throw')
		tags = data.get('tags')
		comment = data.get('comment')
		captcha_answer = data.get('captcha_answer')

		if not prop_type:
			return jsonify({'error': 'Prop type is required'}), 400
		
		if not name and not siteswap_x:
			return jsonify({'error': 'Either name or siteswap_x is required'}), 400

		# Verify Captcha if not already solved
		if not session.get('captcha_solved'):
			captcha_index = session.get('captcha_index')
			if captcha_index is None or captcha_index < 0 or captcha_index >= len(CAPTCHA_QUESTIONS):
				return jsonify({'error': 'Captcha session expired. Please refresh.'}), 400
			
			from hardcoded_database.captcha import is_correct_answer
			if not is_correct_answer(captcha_index, captcha_answer):
				return jsonify({'error': 'Incorrect security answer'}), 400

			# Mark captcha as solved for this session
			session['captcha_solved'] = True
			session.pop('captcha_index', None)

		success = db_manager.add_trick_suggestion(
			prop_type=prop_type,
			name=name,
			siteswap_x=siteswap_x,
			props_count=props_count,
			difficulty=difficulty,
			max_throw=max_throw,
			tags=tags,
			comment=comment
		)

		if success:
			return jsonify({'message': 'Trick suggestion added successfully'}), 200
		else:
			return jsonify({'error': 'Failed to add trick suggestion'}), 500

	except Exception as e:
		print('Error in /api/suggest_trick:', e)
		return jsonify({'error': str(e)}), 500

@api.route('/shorten_url', methods=['POST'])
def shorten_url():
	return "currently unsupported, in the process of building", 500
	# long_url = request.json.get('long_url')
	# if not long_url:
	#     return jsonify({"error": "long_url is required"}), 400
	# try:
	#     code = get_or_create_short_url(long_url)
	#     short_url = url_for('redirect_to_long_url', code=code, _external=True)
	#     return jsonify({"short_url": short_url, "code": code}), 200
	# except Exception as e:
	#     return jsonify({"error": str(e)}), 500
	
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
				main_props=MAIN_PROPS)

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

@app.route('/contribute/add_tricks')
def add_tricks():
	db_connected = False
	try:
		conn = db_manager.connection
		if conn:
			db_connected = True
			conn.close()
	except Exception:
		pass

	return render_template('add_tricks.html',
						 prop_options=list(Prop),
						 tag_category_map=TAG_CATEGORY_MAP_JSON,
						 tag_categories=list(TagCategory),
						 props_settings=ALL_PROPS_SETTINGS_JSON,
						 main_props=MAIN_PROPS,
						 MAX_TRICK_PROPS_COUNT=13,
						 db_connected=db_connected)

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

# Admin Routes
ADMIN_PASSWORD_HASH = 'scrypt:32768:8:1$poumJf7ovURR4H2f$59e5a0ce5fea62a77c97e77e7e8383e0fb7f60c14044ecc6082a1d96deebb0d84a657b9bd4da9fa7bb5e8cd932061e5b6e3c247521671e65b89b634e43080fb3'

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session.get('logged_in'):
			return redirect(url_for('admin_login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
	if request.method == 'POST':
		password = request.form.get('password')
		if check_password_hash(ADMIN_PASSWORD_HASH, password):
			session['logged_in'] = True
			next_url = request.args.get('next')
			return redirect(next_url or url_for('admin_suggestions'))
		else:
			flash('Invalid password', 'error')
	return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
	session.pop('logged_in', None)
	return redirect(url_for('home'))

@app.route('/admin/suggestions')
@login_required
def admin_suggestions():
	return render_template('admin/suggestions.html',
						 prop_options=list(Prop),
						 main_props=MAIN_PROPS,
						 props_settings=ALL_PROPS_SETTINGS_JSON)

@app.route('/admin/api/suggestions/<prop_type>')
@login_required
def get_suggestions(prop_type):
	suggestions = db_manager.get_suggestions(prop_type)
	return jsonify(suggestions)

@app.route('/admin/api/export_suggestions/<prop_type>')
@login_required
def export_suggestions(prop_type):
	import csv
	import io
	
	suggestions = db_manager.get_suggestions(prop_type)
	
	output = io.StringIO()
	writer = csv.writer(output)
	writer.writerow(['name', 'props_count', 'difficulty', 'tags', 'comment', 'max_throw', 'siteswap_x'])
	
	for s in suggestions:
		writer.writerow([s['name'], s['props_count'], s['difficulty'], s['tags'], s['comment'], s['max_throw'], s['siteswap_x']])
		
	output.seek(0)
	return Response(
		output,
		mimetype="text/csv",
		headers={"Content-Disposition": f"attachment;filename=suggestions_{prop_type}.csv"}
	)

@app.route('/admin/api/delete_suggestions/<prop_type>', methods=['POST'])
@login_required
def delete_suggestions(prop_type):
	password = request.json.get('password')
	if not check_password_hash(ADMIN_PASSWORD_HASH, password):
		return jsonify({'error': 'Invalid password'}), 403
		
	success = db_manager.delete_suggestions(prop_type)
	if success:
		return jsonify({'message': 'Suggestions deleted successfully'})
	else:
		return jsonify({'error': 'Failed to delete suggestions'}), 500


@app.route('/siteswap_x')
def siteswap_x():
		  return render_template('siteswap_x.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_game():
	"""Two-round trick verification game."""

	if request.method == 'GET':
		# Initialize Round 1
		session.clear()
		session['verification_session_id'] = str(uuid.uuid4())
		session['verification_round'] = 1
		session['verification_prop'] = 'balls'

		# Generate obvious pair (easy vs hard)
		easy, hard = select_obvious_pair(Prop.Balls)
		trick_left, trick_right, correct = randomize_order(easy, hard)

		# Store in session
		session['verification_trick_left'] = trick_left.to_dict()
		session['verification_trick_right'] = trick_right.to_dict()
		session['verification_correct_position'] = correct

		return render_template(
			'verify.html',
			trick_left=trick_left,
			trick_right=trick_right,
			prop_type='balls',
			round_number=1
		)

	elif request.method == 'POST':
		selected = request.form.get('selected_trick')  # 'left' or 'right'
		current_round = session.get('verification_round', 1)

		if current_round == 1:
			# Validate Round 1
			correct_position = session.get('verification_correct_position')
			round1_passed = (selected == correct_position)
			session['verification_round1_passed'] = round1_passed

			# Store Round 1 data for logging
			session['verification_round1_data'] = {
				'trick_left': session['verification_trick_left'],
				'trick_right': session['verification_trick_right'],
				'correct_position': correct_position,
				'user_selected': selected
			}

			# Generate Round 2 pair (random)
			trick1, trick2 = select_random_pair(Prop.Balls)
			trick_left, trick_right, _ = randomize_order(trick1, trick2)

			session['verification_trick_left'] = trick_left.to_dict()
			session['verification_trick_right'] = trick_right.to_dict()
			session['verification_round'] = 2

			return render_template(
				'verify.html',
				trick_left=trick_left,
				trick_right=trick_right,
				prop_type='balls',
				round_number=2
			)

		elif current_round == 2:
			# Log Round 2 result
			log_verification_result(
				session_data={
					'session_id': session.get('verification_session_id'),
					'round1_passed': session.get('verification_round1_passed'),
					'round1_data': session.get('verification_round1_data'),
					'round2_data': {
						'trick_left': session['verification_trick_left'],
						'trick_right': session['verification_trick_right']
					}
				},
				round2_choice=selected
			)

			# Clear session and redirect to home
			session.clear()
			return redirect(url_for('home'))

	# Fallback: redirect to GET
	return redirect(url_for('verify_game'))

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
