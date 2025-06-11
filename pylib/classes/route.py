from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import zlib
from base64 import b64encode, b64decode

from pylib.classes.prop import Prop
from pylib.classes.trick import Trick


DEFAULT_ROUTE_DURATION_SECONDS = 600  # 10 minutes
DEFAULT_QUALIFICATIONS_ROUTE_DURATION_SECONDS = 1800  # 30 minutes

@dataclass(kw_only=True)
class Route:
    name: str
    prop: Prop
    duration_seconds: int = DEFAULT_ROUTE_DURATION_SECONDS  # Seconds
    
    # Dict[props_count: tricks]
    tricks: List[Trick]
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'prop': self.prop.value,
            'duration_seconds': self.duration_seconds,
            'tricks': [{
                'name': trick.name,
                'props_count': trick.props_count,
                'difficulty': trick.difficulty,
                'tags': [str(tag) for tag in trick.tags] if trick.tags else [],
                'comment': trick.comment
            } for trick in self.tricks]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Route':
        return cls(
            name=data['name'],
            prop=Prop.get_key_by_value(data['prop']),
            duration_seconds=data['duration_seconds'],
            tricks=[Trick.from_dict(trick) for trick in data['tricks']]
        )
        

    def serialize(self) -> str:
        # Convert to dict, then to JSON, compress with zlib, and encode in base64
        route_dict = self.to_dict()
        json_str = json.dumps(route_dict)
        compressed = zlib.compress(json_str.encode('utf-8'))
        return b64encode(compressed).decode('utf-8')

    @classmethod
    def deserialize(cls, serialized: str) -> 'Route':
        try:
            # Decode base64, decompress with zlib, parse JSON, and create Route
            compressed = b64decode(serialized.encode('utf-8'))
            json_str = zlib.decompress(compressed).decode('utf-8')
            data = json.loads(json_str)
            return cls.from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to deserialize route: {str(e)}")
