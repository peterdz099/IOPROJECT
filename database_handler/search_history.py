from database_handler.initialize_database import Database
from mysql.connector import Error


class SearchHistory:
    def __init__(self, database: Database):
        self.connection = database.get_connection()

    def add_search_history(self, user_id, user_input):
        insert_search_history_query = """
                INSERT INTO search_history
                (user_id, user_input, datetime) 
                VALUES (%s, %s, NOW())
                """

        search_history_record = (user_id, user_input)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_search_history_query, search_history_record)
                self.connection.commit()
        except Error as e:
            print(e)

    def select_search_history(self, user_id) -> list[dict]:
        select_search_history_query = """
                        SELECT * FROM search_history
                        WHERE user_id = %s
                        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_search_history_query, (user_id,))
                output = []
                fetched_records = cursor.fetchall()
                if fetched_records is not None:
                    for row in fetched_records:
                        record = {'user_id': row[0], 'user_input': row[1], 'datetime': row[2]}
                        output.append(record)
                    return output
                else:
                    raise Error('No search history found')
        except Error as e:
            print(e)
