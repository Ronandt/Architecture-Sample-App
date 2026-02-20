
from repository import ItemRepository
from app.shared.exceptions import InvalidItemTitle, InvalidItemDescription

class ItemService:
    """Business logic layer for Items."""

    def __init__(self, repository):
        self.repository = repository
    def create_item(self, title, description, keycloak_user_id: str):
        sanitised_title = title.strip()
        sanitised_description = description.strip()
        if(len(sanitised_title) > 30):
            raise InvalidItemTitle("Title exceeds 30 characters")
        elif len(sanitised_title) == 0:
            raise InvalidItemTitle("Title must have more than 0 characters")
        elif len(sanitised_description == 0):
            raise InvalidItemDescription("Description must have more than 0 characters")
        elif(len(sanitised_description) > 100):
            raise InvalidItemDescription("Description exceeds 100 characters")
        return self.repository.create_item(
            sanitised_title,
            sanitised_description,
            owner_id=keycloak_user_id
        )


    def get_user_items(self, keycloak_user_id: str):
        return self.repository.get_items_for_user(keycloak_user_id)