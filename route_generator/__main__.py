from route_generator.prop import Prop
from route_generator.route_generator import generate_route
from route_generator.tricks.tags import Tag


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
    
    props_count = set()
    route_lines = []
    for trick in route:
        if trick.props_count not in props_count:
            route_lines.append(f"#### {trick.props_count} {prop.value} ####")
            props_count.add(trick.props_count)
        route_lines.append(trick.name)
        
    print("\n".join(route_lines))