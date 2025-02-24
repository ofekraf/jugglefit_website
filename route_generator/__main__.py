from .prop import Prop
from .route_generator import generate_route
from .tricks.tags import Tag


if __name__ == "__main__":
    prop = Prop.Rings
    route = generate_route(
        prop=prop,
        min_props=3,
        max_props=5,
        min_difficulty=0,
        max_difficulty=100,
        route_length=2,
        excluded_tags={Tag.Siteswap}
    )
    
    route_lines = []
    for props_count, tricks in route.items():
        route_lines.append(f"#### {props_count} {prop.value} ####")
        for trick in tricks:
            route_lines.append(trick.name)
        
    print("\n".join(route_lines))