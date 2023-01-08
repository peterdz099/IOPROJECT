from database_handler.initialize_database import Database
from mysql.connector import Error


class Offers:
    def __init__(self, database: Database):
        self.connection = database.get_connection()

    def add_offer(self, offer_id, url, toy_id, shop_id, shop_name, price):
        insert_offer_query = """
                INSERT IGNORE INTO offers 
                (id, url, toy_id, shop_id, shop_name, price) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """

        offer_record = (offer_id, url, toy_id, shop_id, shop_name, price)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_offer_query, offer_record)
                self.connection.commit()
        except Error as e:
            print(e)

    def select_offer(self, offer_id):
        select_offer_query = """
                        SELECT * FROM offers
                        WHERE id = %s
                        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_offer_query, (offer_id,))
                output = cursor.fetchone()
                if output is not None:
                    return {'id': output[0], 'url': output[1], 'toy_id': output[2], 'shop_id': output[3],
                            'shop_name': output[4], 'price': output[5]}
                else:
                    raise Error('No offer found')
        except Error as e:
            print(e)
