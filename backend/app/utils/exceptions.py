class UserAlreadyInGroupError(Exception):
    def __init__(self, user_id: int, group_id: int):
        self.user_id = user_id
        self.group_id = group_id
        super().__init__(f'User {user_id} already in group {group_id}')

class TaskNotInDatabaseError(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'Task {task_id} not found in database or ID is incorrect')

class GroupNotInDatabaseError(Exception):
    def __init__(self, group_id: int):
        self.group_id = group_id
        super().__init__(f'Group {group_id} not found')

class UserNotInGroupError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f'User {user_id} not in group')

class UserHaveNoRightsError(Exception):
    def __init__(self, user_id: int, group_id: int):
        self.user_id = user_id
        self.group_id = group_id
        super().__init__(f'User {user_id} have no rights to do such actions in group {group_id}')

class UserIsGroupCreator(Exception):
    def __init__(self, user_id: int, group_id: int):
        self.user_id = user_id
        self.group_id = group_id
        super().__init__(f'User {user_id} is a creator of group {group_id}')