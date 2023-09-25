import yaml
import logging
from pymongo import MongoClient

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


class DebugConfig:
    """
    A class to manage loading and accessing configuration from a YAML file.

    Attributes:
        file_path (str): The path to the YAML configuration file.

    Methods:
        load_config(): Load and parse the YAML configuration file.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.load_config()

    def load_config(self):
        """
        Load and parse the YAML configuration file.

        Returns:
            dict or None: The parsed configuration as a dictionary, or None if there was an error.
        """
        try:
            with open(self.file_path, "r") as yaml_file:
                self.config = yaml.load(yaml_file, Loader=yaml.FullLoader)
            return self.config
        except FileNotFoundError as e:
            error_logger.error(f"Config file not found: {str(e)}")
            self.config = None
        except yaml.YAMLError as e:
            error_logger.error(f"Error parsing YAML config: {str(e)}")
            self.config = None


class MongoConnector:
    """
    A class to establish and manage connections to MongoDB.

    Attributes:
        config (dict): Configuration for connecting to MongoDB.

    Methods:
        connect(): Establish a connection to MongoDB.
        close(): Close the MongoDB connection.
    """

    def __init__(self, config):
        self.config = config
        self.client = None
        self.collection = None

    def connect(self):
        """
        Establish a connection to MongoDB.

        Returns:
            None
        """
        try:
            self.client = MongoClient(self.config["mongo_name"])
            db = self.client[self.config["mongo_db"]]
            self.collection = db[self.config["mongo_collection"]]
        except Exception as e:
            error_logger.error(f"Error connecting to MongoDB: {str(e)}")

    def close(self):
        """
        Close the MongoDB connection.

        Returns:
            None
        """
        if self.client:
            self.client.close()


class MongoDataManager:
    """
    A class to manage interactions with MongoDB for data storage.

    Methods:
        save_data(data): Save data to MongoDB.
    """

    def __init__(self):
        config_object = DebugConfig("database/config.yml")
        config = config_object.load_config()
        self.mongo_connector = MongoConnector(config)

    def save_data(self, data):
        """
        Save data to MongoDB.

        Args:
            data (dict): The data to be saved in MongoDB.

        Returns:
            None
        """
        try:
            self.mongo_connector.connect()
            self.mongo_connector.collection.insert_one(data)
            self.mongo_connector.close()
        except Exception as e:
            error_logger.error(f"Can't able to save data in MongoDB: {str(e)}")

    def delete_data(self, conversation_index):
        """
        Delete data from MongoDB based on filter criteria.

        Args:
            filter_criteria (dict): The filter criteria for deleting records.

        Returns:
            bool: True if records were deleted, False otherwise.
        """
        try:
            filter_criteria = {"conversation_index": conversation_index}
            self.mongo_connector.connect()
            result = self.mongo_connector.collection.delete_one(filter_criteria)
            self.mongo_connector.close()
            if result.deleted_count > 0:
                return True  # Records were deleted
            else:
                return False  # No matching records found
        except Exception as e:
            error_logger.error(f"Can't delete data in MongoDB: {str(e)}")
            return False  # Error occurred while deleting

    def update_data(self, target_conversation_index, new_data):
        """
        Update data in MongoDB based on the record ID.

        Args:
            record_id (str): The ID or unique identifier of the record to update.
            new_data (dict): The updated data to replace the existing data.

        Returns:
            bool: True if the record was updated, False otherwise.
        """
        try:
            update_operation = {"$set": new_data}
            self.mongo_connector.connect()
            result = self.mongo_connector.collection.update_one(
                {"conversation_index": target_conversation_index}, update_operation
            )
            self.mongo_connector.close()
            if result.modified_count > 0:
                return True  # Record was updated
            else:
                return False  # No matching record found for update
        except Exception as e:
            error_logger.error(f"Can't update data in MongoDB: {str(e)}")
            return False  # Error occurred while updating
