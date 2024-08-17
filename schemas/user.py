# def userEntity(item) -> dict:
#     return {
#         "id": str(item["_id"]),
#         "name" : item["name"],
#         "email" : item["email"],
#         "password" : item["password"]
#     }

# def usersEntity(entity) -> list:
#     return [userEntity(item) for item in entity]

def serializeDict(item) -> dict:
    return {
        **{i: str(item[i]) for i in item if i == "_id"},
        **{i: str(item[i]) for i in item if i != "_id"},
    }

def serializeList(entity) -> list:
    return [serializeDict(item) for item in entity]
