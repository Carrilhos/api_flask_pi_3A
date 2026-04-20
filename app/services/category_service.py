from app.repositories.category_repository import (
    find_all_categories,
    find_category_by_id
)

def get_all_categories():
    categories = find_all_categories()
    return categories

def get_category_by_id(id_category):
    category = find_category_by_id(id_category)

    if not category:
        return None

    return category