import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:root@localhost:5432', self.database_name) # I used CREATE DATABASE trivia_test TEMPLATE trivia to duplicate the main DB
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

    def test_get_api_endpoints(self):
        res = self.client().get('/api')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['briefing'])
        self.assertTrue(data['endPoints'])
        self.assertEqual(data['success'], True)

    def test_get_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['categories'])
        self.assertEqual(data['success'], True)
    
    def test_get_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['categories'])
        self.assertTrue(data['currentCategory']) # Again not sure why is this even needed but will check against it anyway
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['success'], True)

    def test_delete_question(self):
        test_question = Question.query.all()[-1] #Last question
        res = self.client().delete(f'/api/questions/{test_question.id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['deleted'], test_question.id)
        self.assertEqual(data['success'], True)
    
    def test_delete_nonexistent_question(self):
        test_question_id = 13112221 # Look-and-See sequence
        res = self.client().delete(f'/api/questions/{test_question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
    
    def test_post_question(self):
        test_question = {
            'question' : 'Who is the author for the novel series (Overlord)?',
            'answer' : 'Kugane Maruyama',
            'category' :  5,
            'difficulty' : 4
        }
        res = self.client().post('/api/questions', json=test_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['created'])
        self.assertEqual(data['success'], True)
    
    def test_post_question_empty_field(self):
        test_question = {
            'question' : 'Who is the author for the novel series (Overlord)?',
            'answer' : '',
            'category' :  5,
            'difficulty' : 4
        }
        res = self.client().post('/api/questions', json=test_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
    
    def test_post_question_missing_field(self):
        test_question = {
            'question' : 'Who is the author for the novel series (Overlord)?',
            'category' :  5,
            'difficulty' : 4
        }
        res = self.client().post('/api/questions', json=test_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
    
    def test_search_question(self):
        search_term = {
            'searchTerm' : 'novel'
        }
        res = self.client().post('/api/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['categories'])
        self.assertEqual(data['currentCategory'],0)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['success'], True)
    
    def test_search_question_no_keyword(self):
        search_term = {
            'searchTerm' : ''
        }
        res = self.client().post('/api/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
    
    def test_search_question_no_json_key(self):
        search_term = {}
        res = self.client().post('/api/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)
    
    def test_get_questions_by_category(self):
        res = self.client().get('/api/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['currentCategory'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['success'], True)

    def test_get_questions_by_invalid_category(self):
        res = self.client().get('/api/categories/66/questions') #Order 66. Eliminate the Jedi order!
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)

    def test_get_quiz_questions(self):
        test_quiz = {
            'previous_questions' : [1,2],
            'quiz_category' : {'id' : 1}
        }
        res = self.client().post('/api/quizzes', json=test_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['question'])
        self.assertEqual(data['success'], True)

    def test_get_quiz_questions_no_json_key(self):
        test_quiz = {
            'previous_questions' : [1,2]
        }
        res = self.client().post('/api/quizzes', json=test_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)

    def test_get_quiz_questions_no_category_id(self):
        test_quiz = {
            'previous_questions' : [1,2],
            'quiz_category' : {}
        }
        res = self.client().post('/api/quizzes', json=test_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)

    def test_get_quiz_questions_invalid_category_id(self):
        test_quiz = {
            'previous_questions' : [1,2],
            'quiz_category' : {'id' : 50}
        }
        res = self.client().post('/api/quizzes', json=test_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()