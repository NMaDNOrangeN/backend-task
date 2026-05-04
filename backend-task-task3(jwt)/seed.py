import models
from security import get_password_hash

models.db.create_db_and_tables()

with models.db.Session(models.db.engine) as s:
    s.add(models.Priority(name="Low"))
    s.add(models.Priority(name="Medium"))
    s.add(models.Priority(name="High"))
    s.add(
        models.User(
            username="admin",
            hashed_password=get_password_hash("Admin123"),
            is_admin=True,
        )
    )
    s.commit()
