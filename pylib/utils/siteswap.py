def parse_siteswap_x(pattern):
    """
    Parse a Siteswap X pattern string into a list of dicts with number, mod, and catch_mod.
    Example: '53{U/P}4{S}' -> [
        {'number': '5', 'mod': None, 'catch_mod': None},
        {'number': '3', 'mod': 'U', 'catch_mod': 'P'},
        {'number': '4', 'mod': 'S', 'catch_mod': None}
    ]
    Multi-digit numbers are split so that modifiers only apply to the last digit.
    """
    import re
    result = []
    # Pattern: single char (digit or letter) {mod/catch_mod}
    token_re = re.compile(r'([0-9a-zA-Z])(?:\{([^}/]*)(?:/([^}]*))?\})?')
    for m in token_re.finditer(pattern):
        number = m.group(1)
        mod = m.group(2) if m.group(2) else None
        catch_mod = m.group(3) if m.group(3) else None
        result.append({'number': number, 'mod': mod, 'catch_mod': catch_mod})
    return result

def render_siteswap_x(pattern):
    """
    Render a Siteswap X pattern as HTML, with each part as a span for styling in the template.
    Returns a Markup string for safe HTML rendering in Jinja2.
    """
    from markupsafe import Markup, escape
    parts = parse_siteswap_x(pattern)
    html = ''
    for part in parts:
        html += '<span class="siteswap-x-throw">'
        if part['mod']:
            html += f'<span class="siteswap-x-throw-mod">{escape(part["mod"])}</span>'
        else:
            html += '<span class="siteswap-x-throw-mod">&nbsp;</span>'
        html += f'<span class="siteswap-x-number">{escape(part["number"])}</span>'
        if part['catch_mod']:
            html += f'<span class="siteswap-x-catch-mod">{escape(part["catch_mod"])}</span>'
        html += '</span>'
    return Markup(html)
