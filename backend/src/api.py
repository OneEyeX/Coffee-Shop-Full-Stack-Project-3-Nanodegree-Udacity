from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# uncomment this line below before testing with POSTMAN
# db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


# get ALL the drinks (without details)
@app.route('/drinks', methods=['GET'])
def get_drinks():
    # query the database
    drinks_query = Drink.query.all()

    # transform drinks to short representation form (without details)
    drinks = [drink.short() for drink in drinks_query]

    # return a success response and the drinks list
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


# get ALL the drinks (with details)
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    # query the database
    drinks_query = Drink.query.all()

    # transform drinks to long representation form (with details)
    drinks = [drink.long() for drink in drinks_query]
    # return a success response and the drinks list
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


# ADD a drink
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    # retrieve the user inputs
    body = request.get_json()

    title = body.get('title') or None
    recipe = body.get('recipe') or None
    # make sure all inputs are present
    # abort if one of the inputs is missing
    if title is None or recipe is None:
        abort(400)

    try:
        # check the recipe type
        if type(recipe) is dict:
            recipe = [recipe]

        # create a drink and add it to the database
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()

        # return a success response and the new drink informations
        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })

    # abort if something went wrong
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


# Modify a specific drink
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):

    # query the database for the drink with the given id
    drink_to_update = Drink.query.filter(Drink.id == drink_id).one_or_none()
    # abort if drink is not found
    if not drink_to_update:
        abort(404)

    # retrieve the user inputs
    body = request.get_json()
    # else, try to update the drink informations
    try:
        title = body.get('title') or None
        recipe = body.get('recipe') or None

        # if there is a new title update it else just keep the existing title
        if title is not None:
            drink_to_update.title = title

        # if there is a new recipe update it else just keep the existing recipe
        if recipe is not None:
            # drink.recipe = json.dumps(body['recipe'])
            drink_to_update.recipe = json.dumps(recipe)

        drink_to_update.update()

        # return a success response and the updated drink informations
        return jsonify({
            'success': True,
            'drinks': [drink_to_update.long()]
        }), 200

    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# delete a drink
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    # query the database
    drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()
    # if the drink is not found abort the operation
    if drink_to_delete is None:
        abort(404)
    # else, try to delete the drink
    try:
        drink_to_delete.delete()

        # return a success response and the deleted drink id
        return jsonify({
            'success': True,
            'delete': drink_to_delete.id
        }), 200
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


# bad request error handler
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400


# unauthorized error handler
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized Permission denied'
    }), 401


'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


# not found resources error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }), 404


# unallowed method error handler
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405


# Unprocessable request error handler
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


# Server error handler
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code
