import csv
from pylib.classes.trick import Trick
from pylib.classes.tag import Tag
from typing import List, Set


def _parse_tags(tags_str: str, trick_name: str, csv_path) -> Set[Tag]:
	tags = set()
	if not tags_str:
		return tags
	for tag_str in tags_str.split('|'):
		tag_str = tag_str.strip()
		if not tag_str:
			continue
		try:
			tags.add(Tag.get_key_by_value(tag_str))
		except ValueError as e:
			raise ValueError(f"Invalid tag value '{tag_str}' for trick '{trick_name}' in {csv_path}") from e
	return tags


def _int_or_none(value):
	value = (value or '').strip()
	return int(value) if value else None


def load_tricks_from_csv(csv_path) -> List[Trick]:
	"""Load the hardcoded tricks of one prop from its CSV file.

	Columns: name, props_count, difficulty, tags ('|' separated), comment,
	max_throw, siteswap_x. Rows with more columns than the header raise,
	so a stray comma cannot silently drop data.
	"""
	tricks = []
	with open(csv_path, newline='', encoding='utf-8') as csvfile:
		reader = csv.DictReader(csvfile)
		for line_no, row in enumerate(reader, start=2):
			if None in row:
				raise ValueError(f"{csv_path}:{line_no}: too many columns: {row[None]}")
			name = (row.get('name') or '').strip() or None
			tricks.append(Trick(
				name=name,
				props_count=int(row['props_count']),
				difficulty=int(row['difficulty']),
				tags=_parse_tags(row.get('tags'), name, csv_path),
				comment=(row.get('comment') or '').strip(),
				max_throw=_int_or_none(row.get('max_throw')),
				siteswap_x=(row.get('siteswap_x') or '').strip() or None,
			))
	return tricks
