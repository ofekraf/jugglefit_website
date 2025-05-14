from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import zlib
from base64 import b64encode, b64decode
from urllib.parse import unquote

from py_lib.prop import Prop
from py_lib.trick import Trick


DEFAULT_ROUTE_DURATION_SECONDS = 600  # 10 minutes
DEFAULT_PROP = Prop.Balls
DEAFULT_NAME = "My Awesome Route"
DEFAULT_QUALIFICATIONS_ROUTE_DURATION_SECONDS = 1800  # 30 minutes

@dataclass(kw_only=True)
class Route:
    name: Optional[str] = DEAFULT_NAME
    prop: Optional[Prop] = DEFAULT_PROP
    duration_seconds: Optional[int] = DEFAULT_ROUTE_DURATION_SECONDS  # Seconds
    
    tricks: Optional[List[Trick]] = None

    def __post_init__(self):
        if self.tricks is None:
            self.tricks = []
    
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
            # URL decode the serialized string first
            serialized = unquote(serialized)
            
            # Decode base64 and decompress
            compressed = b64decode(serialized)
            json_str = zlib.decompress(compressed).decode('utf-8')
            route_dict = json.loads(json_str)
            return cls.from_dict(route_dict)
        except Exception as e:
            raise ValueError(f"Failed to deserialize route: {str(e)}")
