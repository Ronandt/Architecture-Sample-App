import pytest
from unittest.mock import MagicMock
from features.items.service import ItemService
from shared.exceptions import InvalidItemTitle, InvalidItemDescription, ItemUploadError


def make_item(**kwargs):
    defaults = dict(id=1, title="Test", description="", owner_id="user-1", image_url=None)
    defaults.update(kwargs)
    item = MagicMock()
    for k, v in defaults.items():
        setattr(item, k, v)
    return item


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def s3():
    return MagicMock()


@pytest.fixture
def service(repo, s3):
    return ItemService(repository=repo, s3_client=s3)


@pytest.fixture
def service_no_s3(repo):
    return ItemService(repository=repo, s3_client=None)


# ------------------------------------------------------------------
# create_item
# ------------------------------------------------------------------

class TestCreateItem:
    def test_creates_successfully(self, service, repo):
        repo.create_item.return_value = make_item(title="Hello")
        result = service.create_item("Hello", None, "user-1")
        assert result.title == "Hello"

    def test_strips_whitespace(self, service, repo):
        repo.create_item.return_value = make_item(title="Hello")
        service.create_item("  Hello  ", None, "user-1")
        repo.create_item.assert_called_once_with("Hello", "", "user-1")

    def test_raises_on_empty_title(self, service):
        with pytest.raises(InvalidItemTitle):
            service.create_item("", None, "user-1")

    def test_raises_on_title_too_long(self, service):
        with pytest.raises(InvalidItemTitle):
            service.create_item("a" * 31, None, "user-1")

    def test_raises_on_description_too_long(self, service):
        with pytest.raises(InvalidItemDescription):
            service.create_item("Valid", "x" * 101, "user-1")

    def test_title_at_max_length_is_valid(self, service, repo):
        repo.create_item.return_value = make_item(title="a" * 30)
        service.create_item("a" * 30, None, "user-1")
        repo.create_item.assert_called_once()


# ------------------------------------------------------------------
# upload_file
# ------------------------------------------------------------------

class TestUploadFile:
    def test_raises_when_s3_not_configured(self, service_no_s3):
        with pytest.raises(ItemUploadError, match="not configured"):
            service_no_s3.upload_file(1, "user-1", "file.jpg", b"data", "image/jpeg")

    def test_raises_on_empty_filename(self, service):
        with pytest.raises(ItemUploadError, match="Filename"):
            service.upload_file(1, "user-1", "", b"data", "image/jpeg")

    def test_uploads_and_returns_presigned_url(self, service, repo, s3):
        repo.get_item.return_value = make_item(image_url=None)
        s3.generate_presigned_url.return_value = "http://s3/presigned"
        url = service.upload_file(1, "user-1", "photo.jpg", b"data", "image/jpeg")
        assert url == "http://s3/presigned"
        s3.upload.assert_called_once()
        repo.update_image_url.assert_called_once()

    def test_deletes_old_image_before_upload(self, service, repo, s3):
        repo.get_item.return_value = make_item(image_url="items/user-1/1/old.jpg")
        s3.generate_presigned_url.return_value = "http://s3/presigned"
        service.upload_file(1, "user-1", "new.jpg", b"data", "image/jpeg")
        s3.delete.assert_called_once_with("items/user-1/1/old.jpg")


# ------------------------------------------------------------------
# get_item / get_user_items
# ------------------------------------------------------------------

class TestGetItems:
    def test_get_item_returns_response(self, service, repo):
        repo.get_item.return_value = make_item(id=1, title="My Item")
        result = service.get_item(1, "user-1")
        assert result.id == 1
        assert result.title == "My Item"

    def test_get_user_items_returns_list(self, service, repo):
        repo.get_items_for_user.return_value = [make_item(id=1), make_item(id=2)]
        results = service.get_user_items("user-1")
        assert len(results) == 2
