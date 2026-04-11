import folium

print("MAP_VIEW FILE LOADED")


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
        tiles="CartoDB positron"
    )

    # User / pendant position (distinct blue marker)
    folium.Marker(
        [user_location["lat"], user_location["lon"]],
        popup="<b>You</b>",
        icon=folium.Icon(color="blue", icon="user", prefix="fa")
    ).add_to(m)

    # Item markers
    for item in items:
        if not item.last_location:
            continue

        lat = item.last_location["lat"]
        lon = item.last_location["lon"]

        if item.name == focus_item:
            color = "blue"
        elif item.is_lost():
            color = "red"
        else:
            color = "green"

        popup_text = folium.Popup(
            f"""
            <b>{item.name}</b><br>
            Status: {item.state}<br>
            RSSI: {item.last_rssi}<br>
            Distance: {item.last_distance} m
            """,
            max_width=250
        )

        #print("Rendering items:", [item.name for item in items])

        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)

        if item.last_distance:
            folium.Circle(
                location=[lat, lon],
                radius=item.last_distance,
                color=color,
                fill=True,
                fill_opacity=0.15
            ).add_to(m)

    filename = "map.html"
    m.save(filename)

    return filename
