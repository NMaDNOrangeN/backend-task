import models

models.db.create_db_and_tables()

with models.db.Session(models.db.engine) as s:
    s.add(models.Priority(name="Low"))
    s.add(models.Priority(name="Medium"))
    s.add(models.Priority(name="High"))
    s.add(models.User(username="admin", password="Admin123"))
    s.commit()
