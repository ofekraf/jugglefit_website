import csv
from pylib.classes.trick import Trick
from pylib.classes.tag import Tag
from typing import List


def _parse_tags(tags_str: str) -> set:
	tags = set()
	if not tags_str:
		return tags
	for tag_str in tags_str.split('|'):
		tag_str = tag_str.strip()
		if not tag_str:
			continue
		tag = Tag.get_key_by_value(tag_str)
		tags.add(tag)
	return tags


def load_tricks_from_db(prop_type: str) -> List[Trick]:
	"""Load master tricks for one prop from SQLite.

	Imported lazily to avoid a cycle (db_manager → hardcoded_database.consts
	is fine, but the registry that calls this also lives under
	hardcoded_database).
	"""
	from database.db_manager import db_manager

	tricks: List[Trick] = []
	for row in db_manager.get_tricks(prop_type):
		tricks.append(Trick(
			name=row['name'] or None,
			props_count=row['props_count'],
			difficulty=row['difficulty'],
			tags=_parse_tags(row.get('tags', '')),
			comment=row.get('comment') or '',
			max_throw=row.get('max_throw'),
			siteswap_x=row.get('siteswap_x') or None,
		))
	return tricks


def load_tricks_from_csv(csv_path: str) -> List[Trick]:
	tricks = []
	with open(csv_path, newline='', encoding='utf-8') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			name = row['name']
			props_count = int(row['props_count']) if row['props_count'] else None
			difficulty = int(row['difficulty']) if row['difficulty'] else None
			tags = set()
			if row['tags']:
				for tag_str in row['tags'].split('|'):
					tag_str = tag_str.strip()
					if tag_str:
						tag = Tag.get_key_by_value(tag_str)
						if tag is not None:
							tags.add(tag)
						else:
							raise Exception(f"Invalid tag value {tag_str} for trick {name} in {csv_path}")
			comment = row.get('comment', '')
			max_throw = int(row['max_throw']) if 'max_throw' in row and row['max_throw'] else None
			siteswap_x = row.get('siteswap_x') if 'siteswap_x' in row else None
			tricks.append(Trick(name=name, props_count=props_count, difficulty=difficulty, tags=tags, comment=comment, max_throw=max_throw, siteswap_x=siteswap_x))

	return tricks 