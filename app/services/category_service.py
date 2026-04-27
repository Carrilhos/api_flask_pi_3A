from app.repositories.category_repository import (
    find_all_categories,
    find_category_by_id
)

def get_all_categories():
    """Recupera todas as categorias cadastradas no sistema."""
    categories = find_all_categories()
    return categories

def get_category_by_id(id_category):
    """Recupera uma categoria específica com base no seu ID."""
    category = find_category_by_id(id_category)

    if not category:
        return None

    return category