from mongoengine.queryset.visitor import Q
import requests

class SteamProfileClient(object):
    def __init__(self, db):
        self.sess = requests.Session()
        self.db = db

    def search(self, users, search_string):
        # Using regex to find profiles matching the search string
        # The '^' character ensures the search string matches from the start of the steamid
        regex = f"^{search_string}"
        profiles = users.objects.filter(Q(steamid__iregex=regex) | Q(name__iregex=regex))
        results = [profile for profile in profiles]
        return results