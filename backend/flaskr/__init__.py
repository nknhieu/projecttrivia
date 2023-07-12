import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    questions_count = len(selection)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = min(start + QUESTIONS_PER_PAGE, questions_count)
    current_questions = [question.format() for question in selection[start:end]]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app)
    
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # @app.after_request
    # def after_request(response):
    #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    #     response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
    #     return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    # @app.route('/')
    # def welcome():
    #     return jsonify({
    #         "message":'Healthy',
    #         "status":"OK"
    #     }),200
    
    @app.route("/categories")
    def get_all_categories():
        categories = Category.query.all()
        categories_dict = {}

        for category in categories:
          categories_dict[category.id] = category.type

        response = {
        'success': True,
        'categories': categories_dict
        }

        return jsonify(response)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        try:
            # Get all questions and total number of questions
            selection = Question.query.order_by(Question.id).all()
            total_questions = len(selection)

            # Get current questions for the page
            current_questions = paginate_questions(request, selection)

            # If the page number is not found
            if not current_questions:
                abort(404)

            # Get all categories as a dictionary
            categories_dict = {category.id: category.type for category in Category.query.all()}

            response = {
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': categories_dict
            }

            return jsonify(response)

        except Exception as e:
            print(e)
            abort(400)


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)

            if not question:
                abort(404)

            question.delete()

            return jsonify({
            'success': True
                 })

        except Exception as e:
            print(e)
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=['POST'])
    def add_question():
        try:
            body = request.get_json()

            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)

            if not new_question or not new_answer or not new_category or not new_difficulty:
                abort(400)  # Bad Request

            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except Exception as e:
            print(e)
            abort(422)  # Unprocessable Entity

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    @app.route("/search", methods=['POST'])
    def search():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm')

            if not search_term:
                abort(400)  # Bad Request

            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            if questions:
                current_questions = paginate_questions(request, questions)
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions)
                })

            abort(404)  # Not Found

        except Exception as e:
            print(e)
            abort(422)  # Unprocessable Entity

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
        try:
            category = Category.query.get(id)

            if not category:
                abort(404)  # Not Found

            questions = Question.query.filter_by(category=str(id)).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category.type
            })

        except Exception as e:
            print(e)
            abort(404)  # Not Found

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if quiz_category is None or previous_questions is None:
                abort(400)  # Bad Request

            category_id = quiz_category.get('id')
            questions_query = None

            if category_id == 0:
                questions_query = Question.query
            else:
                questions_query = Question.query.filter_by(category=category_id)

            questions = questions_query.filter(Question.id.notin_(previous_questions)).all()

            if not questions:
                return jsonify({
                    'success': True,
                    'question': None
                })

            random_index = random.randint(0, len(questions) - 1)
            next_question = questions[random_index]

            return jsonify({
                'success': True,
                'question': {
                    'id': next_question.id,
                    'question': next_question.question,
                    'answer': next_question.answer,
                    'category': next_question.category,
                    'difficulty': next_question.difficulty
                }
            })

        except Exception as e:
            print(e)
            abort(422)  # Unprocessable Entity

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_resource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable resource"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method!"
        }), 405


    return app

