
from repository import ItemRepository
from app.shared.exceptions import ItemTitleExceeded,ItemDescriptionExceeded

class ItemService:
    """Business logic layer for Items."""

    def __init__(self, repository):
        self.repository = repository
      


    def create_item(self, title, description, keycloak_user_id: str):
        if(len(title) > 30):
            raise ItemTitleExceeded
        elif(len(description) > 100):
            raise ItemDescriptionExceeded
        return self.repository.create_item(
            title,
            description,
            owner_id=keycloak_user_id
        )


    def get_user_items(self, keycloak_user_id: str):
        return self.repository.get_items_for_user(keycloak_user_id)