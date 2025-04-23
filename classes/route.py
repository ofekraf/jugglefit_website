from dataclasses import dataclass
from typing import Dict, List

from route_generator.prop import Prop
from route_generator.tricks.base_trick import Trick


@dataclass(kw_only=True)
class Route:
    name: str
    prop: Prop
    
    # Dict[props_count: tricks]
    tricks: List[Trick]
    
    def serialize(self) -> str:
        return b64encode(json.dumps(self, default=lambda o: o.__dict__).encode()).decode()

    def unserialize(self, serialized: str) -> 'Route':
        return json.loads(b64decode(serialized.encode()).decode())
