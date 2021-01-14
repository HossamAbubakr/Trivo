import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    def index():
        return redirect(url_for('api'))

    @app.route('/api')
    def api():
        endpoints = {}
        # Took me some time to find that app.url_map.iter_rules holds endpoints data
        for endpoint in app.url_map.iter_rules():
            # Exclude the static, root and main urls
            if ('static' not in endpoint.rule) and (endpoint.rule != '/') and (endpoint.rule != '/api'):
                methods = endpoint.methods
                endpoints[endpoint.rule] = {}
                endpoints[endpoint.rule]['function'] = endpoint.endpoint
                # After a lot of experimentation I found out that you can do inline expression like this! in .net we can do something similar using Linq!
                endpoints[endpoint.rule]['methods'] = list(
                    method for method in methods if method != 'HEAD' and method != 'OPTIONS')
        return jsonify({
            'briefing': 'Welcome to Trivo API, below is the list of the available endpoints, for more information check our documentation file',
            'endPoints': endpoints,
            'success': True
        })

    @app.route('/api/categories')
    def get_categories():
        categories = Category.query.all()
        if len(categories) < 1:  # Assuming that categories must always exist seeing that there is no API to creating them
            abort(
                500, 'Couldn\'t find any categories due to an internal error, please try again later')
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}
        })

    @app.route('/api/questions')
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + 10
        formatted_questions = [question.format() for question in questions]
        categories = {category.id: category.type for category in categories}
        return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'totalQuestions': len(formatted_questions[start:end]),
            'categories': categories,
            'currentCategory': 1
        })

    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            abort(
                422, 'A question with that ID doesn\'t exist, please make sure the ID is correct')
        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(
                500, 'Question deletion failed due to an internal error, please try again later')

    @app.route('/api/questions', methods=['POST'])
    def post_question():
        request_body = request.json
        json_keys = ['question', 'answer', 'category', 'difficulty']
        for json_key in json_keys:  # Easiest way I can think of to search for missing keys
            if (json_key not in request_body.keys()) or ((request_body[json_key]) == ""):
                abort(
                    422, 'One of the required attributes is empty or doesn\'t exist, please refer back to the documentation file')
        category_check = Category.query.filter_by(
            id=request_body.get('category')).all()
        if len(category_check) < 1:
            abort(422, 'Incorrect category ID provided, please try again with a proper ID, remember you can call /api/categories to get the list of categories')
        try:
            question = Question(question=request_body.get('question'),
                                answer=request_body.get('answer'),
                                category=request_body.get('category'),
                                difficulty=request_body.get('difficulty')
                                )
            question.insert()
            return jsonify({
                'success': True,
                'created': question.id})
        except:
            abort(
                500, 'Adding the question failed due to an internal error, please try again later')

    @app.route('/api/questions/search', methods=['POST'])
    def search_questions():
        request_body = request.json
        search_term = request_body.get('searchTerm')
        if (not search_term) and (search_term not in request_body):
            abort(
                422, 'Search attribute can not be blank, please refer back to the documentation file')
        search_pattern = f'%{search_term.strip()}%'
        matching_questions = Question.query.filter(
            Question.question.ilike(search_pattern)).all()
        formatted_questions = [question.format()
                               for question in matching_questions]
        categories = [question['category'] for question in formatted_questions]
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'totalQuestions': len(formatted_questions),
            'categories': categories,
            'currentCategory': 0
        })

    @app.route('/api/categories/<int:category_id>/questions')
    def get_question(category_id):
        questions = Question.query.filter_by(category=category_id).all()
        if len(questions) < 1:
            abort(404, 'No questions found, category is either empty or doesn\'t exist!')
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + 10
        formatted_questions = [question.format() for question in questions]
        currentCategory = Category.query.get(category_id)
        return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'totalQuestions': len(formatted_questions[start:end]),
            'currentCategory': currentCategory.type
        })

    @app.route('/api/quizzes', methods=['POST'])
    def start_quizz():
        request_body = request.json
        previous_questions = request_body.get('previous_questions')
        category = request_body.get('quiz_category')
        if (request_body is None) or ('quiz_category' not in request_body.keys()) or ('id' not in category.keys()):
            abort(
                422, 'quiz category attribute can not be blank, please refer back to the documentation file')
        category_check = Category.query.get(category['id'])
        if category['id'] != 0:
            if category_check == None:
                abort(422, 'Invalid category ID provided, please try again')
        question = Question.query.filter(Question.category == category['id']).filter(
            Question.id.notin_(previous_questions)).first()
        if category['id'] == 0:
            question = Question.query.filter(
                Question.id.notin_(previous_questions)).first()
        if question == None:  # End of questions
            return jsonify({
                'success': True,
            })
        return jsonify({
            'success': True,
            'question': question.format()
        })
    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            # I send custom error messages based on the situation
            "message": str(error)
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": str(error)
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": str(error)
        }), 500

    return app
