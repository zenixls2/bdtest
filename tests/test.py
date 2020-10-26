import pytest
import os
import tempfile
from app import app

@pytest.fixture
def client():
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            app.init_db()

        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

# TODO: need more time for writing unit tests
