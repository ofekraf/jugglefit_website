#!/usr/bin/env python3
"""Convert / modify a serialized juggling route parameter.

The website encodes a :class:`~pylib.classes.route.Route` into a compressed,
base64 string that travels in the URL as ``?route=<serialized>`` (for example on
``/created_route``, ``/run_route`` and ``/live_event``).

This script lets you take such a route (either the raw serialized string or a
full URL containing it) and override one or more route fields, then prints the
new serialized value (and rebuilt URL when a URL was supplied).

Examples
--------
Change the prop to clubs::

    python convert_route.py --route "<serialized-or-url>" --prop clubs

Change the duration to 10 minutes::

    python convert_route.py --route "<serialized-or-url>" --duration 10

Read the route from stdin instead of ``--route``::

    echo "<serialized>" | python convert_route.py --prop rings
"""

import argparse
import os
import sys
from urllib.parse import (
    parse_qs,
    quote,
    unquote,
    urlencode,
    urlparse,
    urlunparse,
)

# Allow running this script directly (e.g. `python scripts/convert_route.py`)
# by ensuring the project root is importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pylib.classes.prop import Prop
from pylib.classes.route import Route


def _extract_route_param(raw: str) -> tuple[str, dict | None]:
    """Return the serialized route string and parsed URL parts (if a URL).

    ``raw`` may be either the bare serialized route or a full URL containing a
    ``route`` query parameter. When a URL is supplied the parsed components are
    returned so the result can be re-assembled into an equivalent URL.
    """

    raw = raw.strip()

    parsed = urlparse(raw)
    if parsed.scheme and parsed.query:
        query = parse_qs(parsed.query, keep_blank_values=True)
        if "route" in query:
            serialized = query["route"][0]
            url_parts = {"parsed": parsed, "query": query}
            return unquote(serialized), url_parts

    # Not a URL (or no route param) - treat the input itself as the route.
    # It may still be percent-encoded, so decode defensively.
    return unquote(raw), None


def _rebuild_url(url_parts: dict, new_serialized: str) -> str:
    """Rebuild a URL with the ``route`` query parameter replaced."""

    parsed = url_parts["parsed"]
    query = url_parts["query"]
    query["route"] = [new_serialized]

    # urlencode with quote_via=quote keeps the encoding consistent with how the
    # site emits these links.
    new_query = urlencode(query, doseq=True, quote_via=quote)
    return urlunparse(parsed._replace(query=new_query))


def _resolve_prop(value: str) -> Prop:
    """Resolve a prop from its enum value (e.g. ``clubs``) or name (``Clubs``)."""

    try:
        return Prop.get_key_by_value(value)
    except ValueError:
        pass

    try:
        return Prop[value]
    except KeyError:
        valid = ", ".join(p.value for p in Prop)
        raise SystemExit(
            f"Invalid prop '{value}'. Valid props: {valid}"
        )


def convert_route(
    serialized: str,
    *,
    prop: str | None = None,
    duration_minutes: float | None = None,
    duration_seconds: int | None = None,
    name: str | None = None,
) -> str:
    """Deserialize, apply overrides, and re-serialize a route."""

    route = Route.deserialize(serialized)

    if prop is not None:
        route.prop = _resolve_prop(prop)

    if duration_minutes is not None:
        route.duration_seconds = int(round(duration_minutes * 60))

    if duration_seconds is not None:
        route.duration_seconds = int(duration_seconds)

    if name is not None:
        route.name = name

    return route.serialize()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Modify a serialized juggling route parameter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--route",
        help="Serialized route string or a full URL containing ?route=... "
        "If omitted, the route is read from stdin.",
    )
    parser.add_argument(
        "--prop",
        help="Override the prop (e.g. 'clubs', 'balls', 'rings', "
        "'club passing').",
    )
    parser.add_argument(
        "--duration",
        type=float,
        metavar="MINUTES",
        help="Override the route duration, in minutes.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=int,
        metavar="SECONDS",
        help="Override the route duration, in seconds (takes precedence over "
        "--duration).",
    )
    parser.add_argument(
        "--name",
        help="Override the route name.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    raw = args.route
    if raw is None:
        raw = sys.stdin.read()

    if not raw or not raw.strip():
        parser.error("No route provided (use --route or pipe via stdin).")

    if (
        args.prop is None
        and args.duration is None
        and args.duration_seconds is None
        and args.name is None
    ):
        parser.error(
            "Nothing to change. Provide at least one of --prop, --duration, "
            "--duration-seconds or --name."
        )

    serialized, url_parts = _extract_route_param(raw)

    try:
        new_serialized = convert_route(
            serialized,
            prop=args.prop,
            duration_minutes=args.duration,
            duration_seconds=args.duration_seconds,
            name=args.name,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(new_serialized)

    if url_parts is not None:
        print(_rebuild_url(url_parts, new_serialized))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
