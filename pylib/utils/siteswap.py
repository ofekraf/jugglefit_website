# Siteswap-X formatter for Jinja filter
import re
from markupsafe import Markup

def format_siteswap_x(siteswap_x: str) -> str:
	"""
	Format a siteswap-x string with modifiers above/below and color-coded.
	Example: '5x*' → '5' (main), 'x' (modifier below), '*' (modifier above)
	Returns HTML string.
	"""
	if not siteswap_x:
		return ''
	# Replace encoded arrows and plain arrows with unicode arrow
	siteswap_x = siteswap_x.replace('-&gt;', '→').replace('->', '→')
	# Support both trailing modifiers (e.g. 10cN3) and curly-brace modifiers (e.g. 3{N})
	from markupsafe import escape
	# Regex: match e.g. 10cN, 3N, 3{S/C}, 3{N}, 10c, 3, etc.
	# 1. Main part: digits/letters/arrows
	# 2. Optional curly modifier: {S/C} or {N}
	# 3. Optional trailing modifier: single uppercase letter or digit
	token_re = re.compile(r'([0-9a-z→]+)(?:\{([^{}\/]*)?(?:/([^{}]*))?\})?([A-Z0-9])?')
	html = ''
	for match in token_re.finditer(siteswap_x):
		main = escape(match.group(1))
		throw_mod = match.group(2) if match.group(2) is not None else ''
		catch_mod = match.group(3) if match.group(3) is not None else ''
		trailing_mod = match.group(4)
		html += '<span class="siteswap-x-digit-container">'
		# Throw modifier (above)
		if throw_mod or trailing_mod:
			above = escape(throw_mod) if throw_mod else escape(trailing_mod) if trailing_mod else ''
			if above:
				html += f'<span class="siteswap-x-throw-mod">{above}</span>'
		# Main digit
		html += f'<span class="siteswap-x-digit">{main}</span>'
		# Catch modifier (below)
		if catch_mod:
			html += f'<span class="siteswap-x-catch-mod">{escape(catch_mod)}</span>'
		html += '</span> '
	return html.strip()

def format_siteswap_x_markup(siteswap_x: str) -> Markup:
	return Markup(format_siteswap_x(siteswap_x))
