from flask_jwt import jwt_required
from flask_restful import Resource, reqparse
import sqlite3

from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This filed cannot be left blank')

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'item {} already created'.format(name)}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name=name, price=data['price'])

        try:
            item.insert()
        except:
            return {"message": "An error occured inserting the item."}, 500

        return item.json(), 201

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name = ?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {'message': 'Item deleted'}

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)
        updated_item = ItemModel(name=name, price=data['price'])
        try:
            if not item:
                updated_item.insert()
            else:
                updated_item.update()
        except:
            return {"message": "An error occured updating the item."}, 500
        return updated_item.json()


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append(ItemModel(name=row[0], price=row[1]))
        connection.close()

        return {'items': [item.json() for item in items]}
