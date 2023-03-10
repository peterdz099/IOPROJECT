from database_handler.initialize_database import Database
from mysql.connector import Error


# Managing shopping_list table
class ShoppingList:
    def __init__(self, database: Database):
        self.connection = database.get_connection()

    def add_shopping_list(self, user_id, offer_id):
        insert_shopping_list_query = """
                INSERT INTO shopping_list
                (user_id, offer_id) 
                VALUES (%s, %s)
                """

        shopping_list_record = (user_id, offer_id)  # arguments passed as query values

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_shopping_list_query, shopping_list_record)
                self.connection.commit()
        except Error as e:
            print(e)

    # Returns shopping_list rows of specified user_id
    def select_shopping_list(self, user_id) -> list[dict]:
        select_shopping_list_query = """
                        SELECT * FROM shopping_list
                        WHERE user_id = %s
                        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_shopping_list_query, (user_id,))  # single variable must be passed in tuple
                output = []
                fetched_records = cursor.fetchall()
                if fetched_records is not None:
                    for row in fetched_records:
                        record = {'user_id': row[0], 'offer_id': row[1]}  # dict containing single row data
                        output.append(record)
                    return output
                else:
                    raise Error('No shopping list found')
        except Error as e:
            print(e)

    # Removes shopping_list rows of specified user_id
    def delete_shopping_list(self, user_id):
        delete_shopping_list_query = """
                DELETE FROM shopping_list
                WHERE user_id = %s
                """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(delete_shopping_list_query, (user_id,))  # single variable must be passed in tuple
                self.connection.commit()
        except Error as e:
            print(e)
