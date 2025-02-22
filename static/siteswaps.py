import random


SITESTWAPS = {2: ['40', '312', '330', '501', '40141'],
              3: ['3', '42', 'shower', '60', '423', '441', '504', '522', '531', '531', '612', '801', '4413', '4440',
                  '5223', '5241', '5313', '6312', '7131', '8040', '42333', '42423', '44133', '45141', '50505',
                  '51234', '51414', '52233', '52512', '53133', '55014', '55500', '81411', '517131', '615150',
                  '5224233', '33333342', '53145305520', 'Mills Mess', 'Back-Crosses', 'Reverse Shoulders',
                  'Neck Throws', 'Half Shower', 'Pirouette'],
              4: ['4', 'Half Shower', '62', '71', '80', '453', '534', '552', '561', '615', '633', '642', '714', '723',
                  '741', '831', '5524', '5551', '6424', '7333', '7531', '53444', '55244', '55514', '55550',
                  '56414', '66161', '68141', '661515', '719151', '7161616', '7272712', 'Shower', 'Overheads',
                  "Shoulder", "Pirouette"],
              5: ['5', '64', '73', '82', '91', '645', '663', '726', '744', '771', '753', '915', '7562', '7571',
                  '66661', '67561', '75751', '77731', '88333', '94444', '95353', '97333', '97441', '97522', '777171',
                  '123456789', '8483848034', '(6x,4)*', '(4x,6)*', '97531', 'Reverse Cascade', "Pirouette"],
              6: ['6', '75', '84', '93', '756', '945'],
              7: ['7', '86', '95', '867', '9955'],
              8: ['8', '97', '978'],
              9: ['9']}


def generate_random_tricks(props_list, include_tricks=None, exclude_tricks=None):
    if include_tricks is None:
        include_tricks = []
    if exclude_tricks is None:
        exclude_tricks = []

    print()
    result = []

    for key, length_of_props in props_list:
        # Get the available tricks for this prop count
        available_tricks = SITESTWAPS.get(key, []).copy()

        # Filter out excluded tricks
        available_tricks = [trick for trick in available_tricks if trick not in exclude_tricks]

        # If there are included tricks, ensure at least one is present
        sampled_values = []
        if include_tricks:
            # Find valid included tricks for this prop count
            valid_included = [trick for trick in include_tricks if trick in available_tricks]
            if valid_included:
                # Ensure at least one included trick is added
                sampled_values.append(random.choice(valid_included))


        # Fill the remaining slots with random tricks
        remaining_slots = length_of_props - len(sampled_values)
        if remaining_slots > 0 and available_tricks:
            # Remove already selected tricks to avoid duplicates
            available_tricks = [trick for trick in available_tricks if trick not in sampled_values]
            if len(available_tricks) >= remaining_slots:
                sampled_values.extend(random.sample(available_tricks, remaining_slots))
            else:
                sampled_values.extend(available_tricks)  # Use all available if not enough

        # If we couldn't fill the required number of tricks, adjust gracefully
        if not sampled_values:
            sampled_values = random.sample(SITESTWAPS.get(key, []), min(length_of_props, len(SITESTWAPS.get(key, []))))

        result.append((key, sampled_values))

    return sorted(result)