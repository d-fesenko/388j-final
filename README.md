# 388j-final

**Description of your final project idea:**

The final project uses the Steam API. This API allows one to retrieve data of a Steam user such as their profile picture, ID, steam level, game library, etc. Any user can search up any Steam user's profile picture. Users can also leave comments on other people's profiles only if a user is logged into the website. In order to login to the website, you must authenticate and login via Steam. The website uses a user's actual Steam's profile background as the website background as well as their profile frame.

**Describe what functionality will only be available to logged-in users:**

As stated before, one can login to comment on other people's profile on the website.

**List and describe at least 4 forms:**

The forms are as followed:
- UserReviewForm: this allows users to type in a review for other profiles
- SearchForm: this allows users to search up another user's profile
- PreferencesForm: this allows users to modify their profile for other users such as making their game library private, making their playtime private, or displaying their profile frame.

**List and describe your routes/blueprints (don’t need to list all routes/blueprints you may have–just enough for the requirement):**

We currently have a logins and users route/blueprint. Logins allows functionality for logging into the website. Users allows functionality for commenting on another user's profile.

**Describe what will be stored/retrieved from MongoDB:**

Profile related data such as username, password, profile picture, steam name. This will be retrieved when logging back into the website.

**Describe what Python package or API you will use and how it will affect the user experience:**

We will be using the Steam API: https://steamapi.xpaw.me/
This will enable a user to research their statistics/badges/any data that is contained for a player.
