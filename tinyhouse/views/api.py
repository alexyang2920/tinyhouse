from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError

from .. import models


@view_config(route_name='users', renderer='json', request_method='GET')
def get_users(request):
    try:
        users = request.dbsession.query(models.User).all()
        return [{'id': user.id, 'name': user.name} for user in users]
    except DBAPIError:
        return Response(json_body={'error': 'Database connection error'}, status='500')


@view_config(route_name='users', renderer='json', request_method='POST')
def create_user(request):
    try:
        name = request.json_body['name']
        role = request.json_body['role']
        newUser = models.User(name=name, role=role)
        request.dbsession.add(newUser)
        return {'message': 'User created successfully'}
    except DBAPIError:
        return Response(json_body={'error': 'Database connection error'}, status='500')
    except KeyError:
        return Response(json_body={'error': 'Invalid input'}, status='400')


@view_config(route_name='users', renderer='json', request_method='GET')
def get_users(request):
    try:
        users = request.dbsession.query(models.User).all()
        return [{'id': user.id, 'name': user.name} for user in users]
    except DBAPIError:
        return Response(json_body={'error': 'Database connection error'}, status='500')
