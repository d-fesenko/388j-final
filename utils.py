import requests
from math import ceil

def get_profile_background(api_key, steam_id):
    url = "https://api.steampowered.com/IPlayerService/GetProfileBackground/v1/"
    params ={
        'key': api_key,
        'steamid': steam_id
    }

    response = requests.get(url, params=params)
    data = response.json()
    imageurl = data.get('response', {}).get('profile_background', {}).get('image_large', "")

    return f"http://media.steampowered.com/steamcommunity/public/images/{imageurl}"

def get_steam_games(api_key, steam_id):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'format': 'json',
        'include_appinfo': True,  #Include game name and logo information
        'include_played_free_games': True  #Include free games the user has played
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    games = data.get('response', {}).get('games', [])
        
    games_details = []
    for game in games:
        name = game.get('name')
        playtime_hours = ceil(game.get('playtime_forever', 0) / 60)  # Convert minutes to hours and round up
        appid = game.get('appid')
        img_icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg" if 'img_icon_url' in game else None
        description = get_game_description(appid)
            
        games_details.append({
            'name': name,
            'playtime_hours': playtime_hours,
            'img_icon': img_icon_url,
            'appid': appid,
            'description': description
        })
        
    return games_details

def get_steam_level(api_key, steam_id):

    url = "https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
    }

    response = requests.get(url, params=params)
    data = response.json()
    level = data.get('response', {}).get('player_level', [])

    return str(level)

def get_game_description(game_id):

    url = "https://store.steampowered.com/api/appdetails?appids=" + str(game_id)

    response = requests.get(url)
    data = response.json()
    description = data.get(str(game_id), {}).get('data', {}).get('short_description', "")

    return description
