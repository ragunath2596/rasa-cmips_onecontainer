import sqlite3
import logging


log_format = (
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s"
)
logging.basicConfig(filename="debug.log", level=logging.DEBUG, format=log_format)

debug_logger = logging.getLogger("debug")
error_logger = logging.getLogger("error")
info_logger = logging.getLogger("info")

debug_handler = logging.FileHandler("debug.log")
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter(log_format))

info_handler = logging.FileHandler("info.log")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(log_format))

error_handler = logging.FileHandler("error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format))

debug_logger.addHandler(debug_handler)
info_logger.addHandler(info_handler)
error_logger.addHandler(error_handler)



def fetch_records_by_provider_number(provider_number):
    """
    This fuction will fetch the reord according to the provider_number
    Args:
        provider_number(String): THis is the string for the provider_number
    Return:
        records(List): list of object that have the matching provider_number
    """
    try:
        with sqlite3.connect("user_database.db") as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM user WHERE provider_number = ?"
            cursor.execute(query, (provider_number,))
            records = cursor.fetchall()

            return records
    except Exception as e:
        error_logger.error(f"Error if fetching record{str(e)}")

 