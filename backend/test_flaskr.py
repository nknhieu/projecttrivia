import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import pytest

from flaskr import create_app
from models import setup_db, Question, Category



class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
def test_get_paginated_questions(client):
    res = client.get('/questions')
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data["success"] is True
    assert data["total_questions"]
    assert len(data["categories"])
    assert len(data["questions"])

def test_get_page_bad_req(client):
    res = client.get('/questions?page=1000')
    data = json.loads(res.data)
    assert res.status_code == 400
    assert data['success'] is False
    assert data['message'] == 'Bad request'

def test_get_categories(client):
    res = client.get('/categories')
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data["success"] is True
    assert data["categories"]

def test_get_categories_not_allowed(client):
    res = client.delete('/categories')
    data = json.loads(res.data)
    assert res.status_code == 405
    assert data["success"] is False

def test_delete_question(client):
    res = client.delete('/questions/1')
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data["success"] is True

def test_delete_question_not_found(client):
    res = client.delete('/questions/10000')
    data = json.loads(res.data)
    assert res.status_code == 404
    assert data["success"] is False
    assert data["message"] == "Page not found"

def test_add_question(client):
    new_question = {
        'question': 'what is your name?',
        'answer': 'Manal',
        'difficulty': 1,
        'category': 1
    }
    res = client.post('/questions', json=new_question)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data["success"] is True

def test_search(client):
    search = {'searchTerm': 'What is'}
    res = client.post('/search', json=search)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data['success'] is True
    assert len(data['questions']) == 10

def test_search_not_found(client):
    search = {'searchTerm': 'whatwow what wowwowwow hehehehe'}
    res = client.post('/search', json=search)
    data = json.loads(res.data)
    assert res.status_code == 404
    assert data['success'] is False
    assert data['message'] == 'Page not found'

def test_questions_in_category(client):
    res = client.get('/categories/1/questions')
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data['success'] is True
    assert len(data['questions']) != 0
    assert data['current_category'] == 'Science'

def test_questions_in_category_not_found(client):
    res = client.get('/categories/100/questions')
    data = json.loads(res.data)
    assert res.status_code == 404
    assert data['success'] is False

def test_quiz(client):
    quiz = {
        'previous_questions': [13],
        'quiz_category': {
            'type': 'Entertainment',
            'id': '3'
        }
    }
    res = client.post('/quizzes', json=quiz)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data['success'] is True
    assert data['question']['category'] == '3'

def test_quiz_not_found_category(client):
    quiz = {
        'previous_questions': [6],
        'quiz_category': {
            'type': 'XXX',
            'id': 'X'
        }
    }
    res = client.post('/quizzes', json=quiz)
    data = json.loads(res.data)
    assert res.status_code == 404
    assert data['success'] is False
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()