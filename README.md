# mal-tools

Some utility scripts that can generate some nice graphs and other things using the [MyAnimeList](https://myanimelist.net) API.

## Scripts

### [get_mal_token.py](get_mal_token.py)

Utility to generate an access token for the [MyAnimeList](https://myanimelist.net) API.

Make sure you have a `.get_mal_token.env` with the following variables:

```
MAL_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
MAL_CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Just run the script and follow the instructions. It will generate a `.env` file with the access token which is then used by the other scripts.

### [related_anime.py](related_anime.py)

Displays a list of all anime that are related in some way or another and orders them by when they aired.

You can specify either `id` or a title query that works similar to the search function on the [MyAnimeList](https://myanimelist.net) website.

Despite being a script, also contains some code that is reused by [anime_graph.py](anime_graph.py). I might want to separate that out at some point.

### [anime_graph.py](anime_graph.py)

Similar to [related_anime.py](related_anime.py), but generates an entire graph of all related anime as an SVG instead.

## Library

### [mal.py](mal.py)

Wraps parts of the [MyAnimeList](https://myanimelist.net) API.
