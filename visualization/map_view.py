import html

import folium

print("MAP_VIEW FILE LOADED")

STATUS_COLOR = {
    "With You": "green",
    "Moving Away": "orange",
    "Left Behind": "red",
    "Not Seen": "gray",
}


def generate_map(map_center, user_location, items, focus_item=None, center_on_user=False):
    """
    map_center = {lat, lon} — Folium map view center
    user_location = {lat, lon} — pendant / GPS for the "You" marker
    items = list of ItemTracker objects
    focus_item = item name to highlight (optional)
    center_on_user = True when map is centered on the user (?center=user)
    """

    zoom = 17 if (focus_item or center_on_user) else 16

    m = folium.Map(
        location=[map_center["lat"], map_center["lon"]],
        zoom_start=zoom,
        tiles="CartoDB positron",
    )

    # User / pendant position (distinct blue marker)
    folium.Marker(
        [user_location["lat"], user_location["lon"]],
        popup="<b>You</b>",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)

    # Item pins only (no distance circles)
    for item in items:
        if not item.last_location:
            continue

        lat = item.last_location["lat"]
        lon = item.last_location["lon"]
        disp = item.display_status

        if item.name == focus_item:
            color = "blue"
        else:
            color = STATUS_COLOR.get(disp, "blue")

        popup = folium.Popup(
            html.escape(f"{item.name} - {disp}"),
            max_width=280,
        )
        tooltip = html.escape(item.name)

        folium.Marker(
            [lat, lon],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)

    filename = "map.html"
    m.save(filename)

    return filename
