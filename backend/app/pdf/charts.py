"""North Indian kundali drawn as SVG.

The North Indian chart is a square cut by its two diagonals and an inner
diamond. The houses never move: house 1 is always the top diamond and the
rest follow anticlockwise. Only the sign numbers change from chart to chart.
"""

from app.astro import constants as c

# Short planet labels, Hindi then English, as printed inside the chart
ABBREVIATIONS = {
    "lagna": ("ल", "Asc"), "sun": ("सू", "Su"), "moon": ("चं", "Mo"), "mars": ("मं", "Ma"),
    "mercury": ("बु", "Me"), "jupiter": ("गु", "Ju"), "venus": ("शु", "Ve"),
    "saturn": ("श", "Sa"), "rahu": ("रा", "Ra"), "ketu": ("के", "Ke"),
}

# For each house (1-12): where the planets are written and where the sign number goes.
# Coordinates are fractions of the chart's width and height.
PLANET_SPOT = [
    (0.50, 0.24), (0.25, 0.105), (0.105, 0.25), (0.25, 0.50), (0.105, 0.75), (0.25, 0.895),
    (0.50, 0.76), (0.75, 0.895), (0.895, 0.75), (0.75, 0.50), (0.895, 0.25), (0.75, 0.105),
]
NUMBER_SPOT = [
    (0.50, 0.445), (0.25, 0.215), (0.215, 0.25), (0.445, 0.50), (0.215, 0.75), (0.25, 0.785),
    (0.50, 0.555), (0.75, 0.785), (0.785, 0.75), (0.555, 0.50), (0.785, 0.25), (0.75, 0.215),
]
# The diamond houses have room for more lines than the corner triangles
ROOMY_HOUSES = (1, 4, 7, 10)

SIZE = 300
LINE = "#7a1f1f"
NUMBER = "#c8781e"
TEXT = "#5a1414"


def chart_points(chart, varga=None):
    """Sign of the Lagna and of every planet, for the birth chart or a divisional chart.

    Returns {key: (sign_index, retrograde)}. The Lagna is missing when the birth time is unknown.
    """
    points = {}
    if varga:
        for key, placed in chart["vargas"][varga].items():
            points[key] = (placed["sign"]["index"], False)
        return points
    if chart["lagna"]:
        points["lagna"] = (chart["lagna"]["sign"]["index"], False)
    for key, planet in chart["planets"].items():
        points[key] = (planet["sign"]["index"], planet["retrograde"])
    return points


def kundali_svg(points, first_sign):
    """Draw one chart. first_sign is the sign placed in house 1 (the Lagna's, or the Moon's)."""
    by_house = {house: [] for house in range(1, 13)}
    for key in ["lagna"] + c.PLANET_KEYS:
        if key not in points:
            continue
        sign, retrograde = points[key]
        hindi, english = ABBREVIATIONS[key]
        label = f"{hindi} {english}" + ("(R)" if retrograde else "")
        by_house[(sign - first_sign) % 12 + 1].append(label)

    s = SIZE
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" class="kundali">',
        f'<rect x="1" y="1" width="{s - 2}" height="{s - 2}" fill="#fffdf6" stroke="{LINE}" stroke-width="2"/>',
        f'<path d="M1 1 L{s - 1} {s - 1} M{s - 1} 1 L1 {s - 1} '
        f'M{s / 2} 1 L{s - 1} {s / 2} L{s / 2} {s - 1} L1 {s / 2} Z" '
        f'fill="none" stroke="{LINE}" stroke-width="1.3"/>',
    ]
    for house in range(1, 13):
        sign_number = (first_sign + house - 1) % 12 + 1
        x, y = NUMBER_SPOT[house - 1]
        parts.append(f'<text x="{x * s:.1f}" y="{y * s:.1f}" class="k-num" fill="{NUMBER}" '
                     f'text-anchor="middle" dominant-baseline="central">{sign_number}</text>')

        labels = by_house[house]
        if not labels:
            continue
        # Shrink the text when a house is crowded
        limit = 4 if house in ROOMY_HOUSES else 2
        font = 12.5 if len(labels) <= limit else max(8.0, 12.5 * limit / len(labels))
        step = font * 1.25
        x, y = PLANET_SPOT[house - 1]
        top = y * s - step * (len(labels) - 1) / 2
        for i, label in enumerate(labels):
            parts.append(f'<text x="{x * s:.1f}" y="{top + i * step:.1f}" class="k-planet" fill="{TEXT}" '
                         f'font-size="{font:.1f}" text-anchor="middle" dominant-baseline="central">{label}</text>')
    parts.append("</svg>")
    return "".join(parts)


def lagna_chart(chart, varga=None):
    points = chart_points(chart, varga)
    return kundali_svg(points, points["lagna"][0])


def moon_chart(chart):
    points = chart_points(chart)
    return kundali_svg(points, points["moon"][0])
