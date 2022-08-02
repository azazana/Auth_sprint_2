from flask import Response, Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api.authorize import authorize
from services.service import (create_new_role,
                      get_role_service, delete_role_service,
                      create_user_role, get_roles_service,
                      delete_user_role_service,get_user_role_service
                      )
#
role = Blueprint('role', __name__)
#

@role.route('/roles_name', methods=['DELETE'])
@jwt_required()
@authorize.has_role('admin')
def delete_role() -> Response:
    """delete role by name
         delete role by name.
         If all ok the role will be deleted
         ---
         parameters:
          - in: header
            name: Authorization
            required: true
            type: string
            description: Authorization token
          - in: query
            name: name
            required: true
            type: string
         responses:
           200:
            description: delete role
            schema:
              id: json_msg
              properties:
                msg:
                  type: string
                  description: message
        """

    name = request.args.get('name')

    return jsonify(delete_role_service(name))


@role.route('/roles', methods=['POST'])
@jwt_required()
@authorize.has_role('admin')
def post_role() -> Response:
    """create role
       create role
        If all ok create and return the role has created
        ---
        parameters:
          - in: header
            name: Authorization
            required: true
            type: string
            description: Authorization token
          - in: query
            name: name
            required: true
            type: string
        responses:
          200:
            description: post role
            schema:
              id: json_msg
            properties:
              msg:
                type: list
                description: message
    """

    name = request.args.get('name')
    return jsonify(create_new_role(name))


@role.route('/roles_name', methods=['GET'])
@jwt_required()
@authorize.has_role('admin')
def get_role() -> Response:
    """get role by name
       get role by name
       If all ok the role will be shown
       ---
       parameters:
          - in: header
            name: Authorization
            required: true
            type: string
            description: session token
          - in: query
            name: name
            required: true
            type: string
       responses:
          200:
           description: get role
           schema:
             id: json_msg
             properties:
           msg:
             type: string
             description: message
    """

    name = request.args.get('name')
    return jsonify(get_role_service(name))


@role.route('/roles', methods=['GET'])
@jwt_required()
@authorize.has_role('admin')
def get_roles() -> Response:
    """get all roles
        Get all roles
        Show all existed role.
        ---
        parameters:
          - in: header
            name: Authorization
            required: true
            type: string
            description: Authorization token
        responses:
          200:
            description: get roles
            schema:
              id: json_msg
              properties:
            msg:
              type: list
              description: message
    """
    return jsonify(get_roles_service())
    # try:
    #     roles = Role.query.all()
    #     if not roles:
    #         return jsonify({"msg": 'no roles'})
    # except Exception:
    #     return jsonify({"msg": 'Error in finding role'})
    # return jsonify(eqrls=[iter.serialize() for iter in roles])


@role.route('/user_roles', methods=['PUT'])
@jwt_required()
@authorize.has_role('admin')
def put_user_role() -> Response:
    """set role to user
       set role to user
       If all ok set role to user in Postgres and return success msg
       ---
       parameters:
          - in: header
            name: Authorization
            required: true
            type: string
            description: Authorization token
          - in: query
            name: name_user
            required: true
            type: string
          - in: query
            name: name_role
            required: true
            type: string
       responses:
         200:
           description: edit role to user
           schema:
             id: json_msg
           properties:
             msg:
               type: list
               description: message
    """
    name_user = request.args.get('name_user')
    role_name = request.args.get('name_role')
    return jsonify(create_user_role(name_user, role_name))


@role.route('/user_roles_delete', methods=['PUT'])
@jwt_required()
@authorize.has_role('admin')
def delete_user_role() -> Response:
    """delete role to user
       delete role to user
       If all ok the role has deleted from user in Postgres and return success msg
       ---
       parameters:
          - in: header
            name: Authorization
            required: true
            type: string
            description: Authorization token
          - in: query
            name: name_user
            required: true
            type: string
          - in: query
            name: name_role
            required: true
            type: string
       responses:
         200:
           description: delete role from user
           schema:
             id: json_msg
           properties:
             msg:
               type: list
               description: message
    """

    name_user = request.args.get('name_user')
    role_name = request.args.get('name_role')
    return jsonify(delete_user_role_service(name_user, role_name))


@role.route('/user_roles', methods=['GET'])
@jwt_required()
@authorize.has_role('admin')
def get_user_role() -> Response:
    """get user's roles
       get user's roles
       Return user's roles
       ---
       parameters:
          - in: header
            name: Authorization
            required: true
            type: string
            description: Authorization token
          - in: query
            name: name_user
            required: true
            type: string
       responses:
         200:
           description: get user's roles
           schema:
             id: json_msg
           properties:
             msg:
               type: list
               description: message
    """
    name_user = request.args.get('name_user')
    return jsonify(eqrls=get_user_role_service(name_user))
