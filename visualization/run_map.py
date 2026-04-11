
from visualization.map_view import generate_map
from core.location import get_current_location
from core.item_manager import ItemManager

def show_map(manager):
    user_location = get_current_location()
    items = manager.all_items()

    generate_map(user_location, user_location, list(items))

    print("Map generated → open map.html")