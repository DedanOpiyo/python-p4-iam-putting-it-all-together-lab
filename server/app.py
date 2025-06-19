#!/usr/bin/env python3

from validate_recipe import ValidateRecipe
from custom_api_exception import APIException

from flask import request, session, jsonify, make_response, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

# Optional: Unauthorize access for all other routes except signup, login and check_session.
# open_access_list, is list of routes that don’t require login.
@app.before_request
def check_if_logged_in():
    open_access_list = [ 
        'signup',
        'login',
        'check_session'
    ]

    if (request.endpoint) not in open_access_list and (not session.get('user_id')):
        return {'error': '401 Unauthorized'}, 401

class Signup(Resource):
    
    def post(self):
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': "No details user provided"}), 400
        
        username = data.get('username')
        password = data.get('password')        

        try:
            new_user = User.create(
                username=username,
                password=password, # Used class method to respect encapsulation
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            
            # new_user.password_hash = password # Create method now handles this

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            
            return make_response(new_user.to_dict(), 201)
        
        except IntegrityError:
            db.session.rollback() # Undo all changes in the transaction - before commit(). Safe recovery - after commit

            return {'error': "422: Username already exists"}, 422
            # return {'error': "422: Unprocessable Entity"}, 422
        
        except:
            return {'error': "422: Unprocessable Entity"}, 422

class CheckSession(Resource):
    
    def get(self):

        user_id = session.get('user_id')

        if user_id:
            
            user = User.query.filter(
                User.id == user_id
            ).first()

            return make_response(user.to_dict(), 200)
        
        else:     
            return {}, 401 # CheckSession # Unauthorized

class Login(Resource):
    
    def post(self): # POST for login
        data = request.get_json()
        
        if not data:
            return jsonify({'error': "No details user provided"}), 400
        
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter(User.username==username).first()

        if user:
            if user.authenticate(password):

                session['user_id'] = user.id

                return make_response(user.to_dict(), 200)
        
        return {'error': "401: Unauthorized"}, 401 # Login

class Logout(Resource):
    
    def delete(self):

        session_active = session.get('user_id')

        if not session_active:
        
            abort(401, description='Unauthorized: No session found.') # Or # return {'error': '401: Unauthorized'}, 401
        
        session['user_id'] = None

        return {}, 204 # Delete # No content

class RecipeIndex(Resource):

    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "401: Unauthorized"}, 401

        user = User.query.filter_by(id=user_id).first()
        if not user: # Must check user
            return {"error": "401: Unauthorized"}, 401 # Users can only view recipes after logging in

        recipes = [
            recipe.to_dict(only=('title', 'instructions', 'minutes_to_complete', 'user'))
            for recipe in user.recipes
        ]

        # recipes = [recipe.to_dict(rules=('-id', '-user_id')) for recipe in Recipe.query.filter(Recipe.user_id==user_id).all()] # We can also get recipes from recipe # Not preferable

        return make_response(jsonify(recipes), 200)

        
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "401: Unauthorized"}, 401

        data = request.get_json()

        ## Optional: A # Validation logic inside routes
        # title = data.get('title')
        # instructions = data.get('instructions')
        # minutes = data.get('minutes_to_complete')

        # # Validation: required fields and rules
        # errors = []
        # if not title:
        #     errors.append("Title is required.")
        # if not instructions or len(instructions.strip()) < 50:
        #     errors.append("Instructions must be at least 50 characters.")
        # if not isinstance(minutes, int) or minutes <= 0:
        #     errors.append("Minutes must be a positive integer.")

        # if errors:
        #     return {"errors": errors}, 422
        
        # Optional: B # Exclude try catch block, its for Test purposes
        try:
            validated = ValidateRecipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=user_id # data.get('user_id') # Avoid getting user id from request body
            )
        except:
            return {"errors": "422: Unprocessable Entity"}, 422

        try:
            new_recipe = Recipe(
                title=validated.title,
                instructions=validated.instructions,
                minutes_to_complete=validated.minutes_to_complete,
                user_id=validated.user_id
            )

            db.session.add(new_recipe)
            db.session.commit()

            return new_recipe.to_dict(only=('title', 'instructions', 'minutes_to_complete', 'user')), 201 # Exclude 'id', too # user - Relationship attribute can be included!

        except Exception as e:
            print("Error creating recipe:", e)
            return {"error": "422: Unprocessable Entity"}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

# Custom error handler
@app.errorhandler(APIException)
def handle_api_exception(e):
    return make_response(jsonify(e.to_dict()), e.status_code)

if __name__ == '__main__':
    app.run(port=5555, debug=True)