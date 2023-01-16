from database_handler.initialize_database import Database
from mysql.connector import Error


class Offers:
    def __init__(self, database: Database):
        self.connection = database.get_connection()

    def add_offer(self, offer_id, toy_name, price, url, shop_name, manufacturer, img_url):
        insert_offer_query = """
                INSERT IGNORE INTO offers 
                (id, toy_name, price, url, shop_name, manufacturer, img_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

        offer_record = (offer_id, toy_name, price, url, shop_name, manufacturer, img_url)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_offer_query, offer_record)
                self.connection.commit()
        except Error as e:
            print(e)

    def select_offer(self, offer_id) -> dict:
        select_offer_query = """
                        SELECT * FROM offers
                        WHERE id = %s
                        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_offer_query, (offer_id,))
                output = cursor.fetchone()
                if output is not None:
                    return {'id': output[0], 'toy_name': output[1], 'price': output[2], 'url': output[3],
                            'shop_name': output[4], 'manufacturer': output[5], 'img_url': output[6]}
                else:
                    raise Error('No offer found')
        except Error as e:
            print(e)
