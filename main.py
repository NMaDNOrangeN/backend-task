from fastapi import FastAPI, HTTPException
import random
from pyd import (
    UserCreate,
    User,
    ItemCreate,
    Item,
    UnfilteredUsers,
    Filters,
    Request,
    Response,
    UserUpdate,
)

app = FastAPI()


@app.post("/users", response_model=User)
def create_users(user: UserCreate):
    new_user = User(
        user_id=random.randint(0, 999),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        age=user.age,
    )
    return new_user


@app.post("/items", response_model=Item)
def create_items(item: ItemCreate):
    new_item = Item(
        name=item.name,
        description=item.description,
        total_price=item.price + (item.price * item.tax / 100),
        tags=item.tags,
        in_stock=item.in_stock,
        quantity=item.quantity,
    )
    return new_item


@app.post("/filter-users", response_model=Response)
def filter_users(request: Request):
    users = request.users
    filters = request.filters

    filtered = []
    for user in users:
        if filters.min_age is not None and user.age < filters.min_age:
            continue
        if filters.max_age is not None and user.age > filters.max_age:
            continue
        if filters.active_only is True and not user.active:
            continue
        filtered.append(user)

    return Response(
        total_input=len(users),
        filtered_count=len(filtered),
        filtered_users=filtered,
        applied_filters=filters,
    )


def random_data():
    return {
        "username": f"user{random.randint(0, 10000)}",
        "email": f"example{random.randint(0, 10000)}@email.com",
        "full_name": f"FirstName{random.randint(0, 10000)} SecondName{random.randint(0, 10000)} LastName{random.randint(0, 10000)}",
        "age": random.randint(18, 120),
    }


@app.put("/users/{user_id}", response_model=User)
def update_users(update_user: UserUpdate):
    data = random_data()

    updated_user = User(
        user_id=random.randint(0, 999),
        username=data["username"],
        email=update_user.email if update_user.email is not None else data["email"],
        full_name=(
            update_user.full_name
            if update_user.full_name is not None
            else data["full_name"]
        ),
        age=update_user.age if update_user.age is not None else data["age"],
    )
    return updated_user
