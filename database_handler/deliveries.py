from database_handler.initialize_database import Database
from mysql.connector import Error


# Managing deliveries table
class Deliveries:
    def __init__(self, database: Database):
        self.connection = database.get_connection()

    def add_delivery(self, price, deliverer, offer_id):
        insert_delivery_query = """
                INSERT INTO deliveries
                (price, deliverer, offer_id) 
                VALUES (%s, %s, %s)
                """

        delivery_record = (price, deliverer, offer_id)  # arguments passed as query values

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_delivery_query, delivery_record)
                self.connection.commit()
        except Error as e:
            print(e)

    # Returns deliveries rows with specified offer_id
    def select_deliveries(self, offer_id) -> list[dict]:
        select_deliveries_query = """
                        SELECT * FROM deliveries
                        WHERE offer_id = %s
                        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_deliveries_query, (offer_id,))
                output = []
                fetched_records = cursor.fetchall()
                if fetched_records is not None:
                    for row in fetched_records:
                        record = {'price': row[0], 'deliverer': row[1],
                                  'offer_id': row[2]}  # dict containing single row data
                        output.append(record)
                    return output
                else:
                    raise Error('No delivery found')
        except Error as e:
            print(e)
