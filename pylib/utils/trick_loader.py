import csv
from pylib.classes.trick import Trick
from pylib.classes.tag import Tag
from typing import List

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
            tricks.append(Trick(name=name, props_count=props_count, difficulty=difficulty, tags=tags, comment=comment))
    return tricks 