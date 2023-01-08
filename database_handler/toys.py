from database_handler.initialize_database import Database
from mysql.connector import Error


class Toys:
    def __init__(self, database: Database):
        self.connection = database.get_connection()

    def add_toy(self, toy_id, name, min_price, manufacturer, num_of_shops, img_url):
        insert_toy_query = """
                INSERT IGNORE INTO toys 
                (id, name, min_price, manufacturer, num_of_shops, img_url) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """

        toys_record = (toy_id, name, min_price, manufacturer, num_of_shops, img_url)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_toy_query, toys_record)
                self.connection.commit()
        except Error as e:
            print(e)

    def select_toy(self, toy_id):
        select_toy_query = """
                        SELECT * FROM toys
                        WHERE id = %s
                        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_toy_query, (toy_id,))
                output = cursor.fetchone()
                if output is not None:
                    return {'id': output[0], 'name': output[1], 'min_price': output[2], 'manufacturer': output[3],
                            'num_of_shops': output[4], 'img_url': output[5]}
                else:
                    raise Error('No toy found')
        except Error as e:
            print(e)
