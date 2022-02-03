
class ConfigParser:

    def __init__(self, path: str):
        self.path = path

    def start(self, option_overrides: dict = None):
        """
        Starts the parsing process.

        :param option_overrides: Dictionary of "overrides." This will match against any setting keys in
                                 global_settings['options'] and override the original value from the config file.
                                 This lets the script prefer script arguments over config settings.
        """
        # TODO: parse config here!!
        pass

    def parse_global_settings(self, g_s: dict):
        """Specifically parses for and updates global_settings from the given dict g_s."""
        # TODO: parse given dictionary of global settings
        pass

    def parse_packs(self, p: dict):
        """Specifically parses for and creates packs from the given dict p."""
        # TODO: parse given dictionary of packs
        pass
