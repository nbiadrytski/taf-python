import configparser
import logging


class ConfigParser:
    """
    Parses data from .ini files.

    Parameters
    ----------
    config_path : str
        Relative path to config

    Attributes
    ----------
    parser : ConfigParser
        ConfigParser object
    """

    def __init__(self, config_path):
        self.parser = configparser.ConfigParser()
        self.parser.read(config_path)
        self.logger = logging.getLogger(__name__)

    def get_section_keys(self, section):
        """
        Returns a dict of section keys.

        Parameters
        ----------
        section : str
            Title of config section

        Returns
        -------
        keys : dict
            Dictionary of section keys
        """
        return dict(self.parser.items(section))

    def get_value(self, section, key):
        """
        Get value by passed section title and its key.

        Parameters
        ----------
        section : str
            Title of config section
        key : str
            Title of section key

        Returns
        -------
        key value : str
            Key value
        """
        try:
            return self.parser.get(section, key)
        except configparser.NoOptionError as error:
            self.logger.error(error)

    def filter_keys(self, title, keys):
        """
        Filter section keys by passed keys.

        Parameters
        ----------
        title : str
            Title of config section
        keys : list or tuple
            Keys to filter

        Returns
        -------
        filtered keys : tuple
            A tuple of filtered keys
        """
        filtered_keys = []

        for key in keys:
            key = self.parser.get(title, key)
            filtered_keys.append(key)

        return tuple(filtered_keys)
