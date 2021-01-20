# Trivo, a Flask trivia game API

## Table of Contents

* [Summary](#Summary)

* [Technologies](#Technologies)

* [Features](#Features)

* [Endpoints](#Endpoints)

* [Documentation](#Documentation)

* [Unit Testing](#Unit-Testing)

* [Usage and Installation](#usage-and-installation)

## Summary

Trivo is a trivia game API that I built to practice full stack programming as part of my udacity nanodegree.

It uses flask as a web framework, PostgreSQL as the database of choice and SqlAlchemy as the ORM

It demonstrates my understanding of API creation, error handling,full documentation and unit testing.

## Technologies

Flask was used as a backend using python.
PostgreSql as the database I used.
SQLAlchemy as the ORM of choice.


## Features

1. Get a list of categories.

2. Get a list of questions in a given category.

3. Search questions.

4. Post question.

5. Delete question.

6. Start playing the game.

## Endpoints 

```json
{
  "briefing": "Welcome to the trivia API, below is the list of the available endpoints, for more information check our documentation file", 
  "endPoints": {
    "/api/categories": {
      "function": "get_categories", 
      "methods": [
        "GET"
      ]
    }, 
    "/api/categories/<int:category_id>/questions": {
      "function": "get_question", 
      "methods": [
        "GET"
      ]
    }, 
    "/api/questions": {
      "function": "post_question", 
      "methods": [
        "POST"
      ]
    }, 
    "/api/questions/<int:question_id>": {
      "function": "delete_question", 
      "methods": [
        "DELETE"
      ]
    }, 
    "/api/questions/search": {
      "function": "search_questions", 
      "methods": [
        "POST"
      ]
    }, 
    "/api/quizzes": {
      "function": "start_quizz", 
      "methods": [
        "POST"
      ]
    }
  }, 
  "success": true
}
```

## Documentation
For a detailed documentation [Full documentation](https://documenter.getpostman.com/view/13571543/TVetc6SC).

## Unit Testing
A test_flask.py file is included that includes a comprehensive list of unit tests.
The PostgreSQL connection string needs to be supplied below
```
self.database_path = "postgres://{}/{}".format('postgres:root@localhost:5432', self.database_name)
```

## Initialization
a psql file is provided **trivia.psql** we a list of initial questions which can be imported to your PostgreSQL instance

## Usage and installation

You can get the project up and running in 3 simple steps.

1. Use the following command to install the required packages
```
pip install -r requirements.txt
```
2. Edit the models.py file and add your PostgreSQL connection string
```
database_path = "postgres://{}/{}".format('CONNECTION_STRING', database_name)
```
3. Use The following command to start the server and voila!
```
set FLASK_APP=flaskr
set FLASK_ENV=development
flask run
```
