from mongoengine.queryset.visitor import Q
import requests

class SteamProfileClient(object):
    def __init__(self, db, users):
        self.sess = requests.Session()
        self.db = db
        self.users = users 

    def search(self, search_string):
        """
        Searches user profiles where the steamid or any other relevant field starts with
        the given search_string using a case-insensitive regex.
        """
        # Using regex to find profiles matching the search string
        # The '^' character ensures the search string matches from the start of the steamid
        regex = f"^{search_string}"
        profiles = self.users(Q(steamid__iregex=regex) | Q(name__iregex=regex))
        results = [profile for profile in profiles]
        return results
