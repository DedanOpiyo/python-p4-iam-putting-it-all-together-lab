# validate_recipe.py
from api_exception import APIException

class ValidateRecipe:
    def __init__(self, title, instructions, minutes_to_complete, user_id):
        errors = []

        if not title:
            errors.append("Title is required.")

        if not instructions or len(instructions.strip()) < 50:
            errors.append("Instructions must be at least 50 characters.")

        if not isinstance(minutes_to_complete, int) or minutes_to_complete <= 0:
            errors.append("Minutes must be a positive integer.")

        if not user_id:
            errors.append("User must be logged in.")

        if errors:
            raise APIException(errors, status_code=422)

        self.title = title
        self.instructions = instructions
        self.minutes_to_complete = minutes_to_complete
        self.user_id = user_id
