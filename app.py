from flask import Flask, render_template, request, jsonify
import stripe
import os
from dotenv import load_dotenv

from database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from database.events.upcoming_events import UPCOMING_EVENTS
from database.organization.affiliates import AFFILIATES
from route_generator.exceptions import NotEnoughTricksFoundException
from route_generator.prop import PROP_OPTIONS, Prop
from route_generator.route_generator import generate_route
from route_generator.tricks.tags import TAG_OPTIONS, Tag

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/')
def home():
    return render_template('index.html', upcoming_events=UPCOMING_EVENTS, last_events=FRONT_PAGE_PAST_EVENTS)


@app.route('/past_events', methods=['GET'])
def past_events():
    return render_template('past_events.html', past_events=ALL_PAST_EVENTS)


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
                name=route_name
            )
        except NotEnoughTricksFoundException:
            return '<p class="no-tricks">No tricks were generated. Try adjusting your criteria.</p>'
        return render_template('created_route.html', route=route)
    return render_template('create_route.html', current_page='create_route', tag_options=TAG_OPTIONS, prop_options=PROP_OPTIONS)

@app.route('/host_event', methods=['GET'])
def host_event():
    return render_template('host_event.html', affiliates=AFFILIATES)

@app.route('/donate', methods=['GET'])
def donate():
    return render_template('donate.html', 
                          current_page='donate',
                          stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'))

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        amount = int(data['amount'])
        currency = data['currency']
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'JuggleFit Donation',
                        'description': 'Support the juggling community',
                    },
                    'unit_amount': amount * 100,  # Convert to smallest currency unit
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + 'donate/success',
            cancel_url=request.host_url + 'donate',
        )
        
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/donate/success')
def donation_success():
    return render_template('donation_success.html', current_page='donate')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)