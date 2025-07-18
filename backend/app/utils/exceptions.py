class UserAlreadyInGroupError(Exception):
    def __init__(self, user_id: int, group_id: int):
        self.user_id = user_id
        self.group_id = group_id
        super().__init__(f'User {user_id} already in group {group_id}')