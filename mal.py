from typing import Literal, Sequence

import dotenv
import httpx

AnimeField = Literal[
    'alternative_titles',
    'average_episode_duration',
    'background',
    'broadcast',
    'created_at',
    'end_date',
    'genres',
    'id',
    'main_picture',
    'mean',
    'media_type',
    'my_list_status',
    'nsfw',
    'num_episodes',
    'num_list_users',
    'num_scoring_users',
    'pictures',
    'popularity',
    'rank',
    'rating',
    'recommendations',
    'related_anime',
    'related_manga',
    'source',
    'start_date',
    'start_season',
    'statistics',
    'status',
    'studios',
    'synopsis',
    'title',
    'updated_at'
]

_env = dotenv.dotenv_values()

if not (access_token := _env['MAL_ACCESS_TOKEN']):
    raise RuntimeError(
        "Invalid MAL_ACCESS_TOKEN; make sure to run get-mal-token.")

if not (refresh_token := _env['MAL_REFRESH_TOKEN']):
    raise RuntimeError(
        "Invalid MAL_REFRESH_TOKEN; make sure to run get-mal-token.")

del _env


def _get_endpoint(endpoint: str) -> str:
    return f'https://api.myanimelist.net/v2/{endpoint}'


async def _get(endpoint, **kwargs) -> dict:
    url = _get_endpoint(endpoint)
    headers = headers = {'Authorization': f'Bearer {access_token}'}
    async with httpx.AsyncClient() as client:
        return (await client.get(url, headers=headers, params=kwargs)).json()


async def list_anime(query: str, /, limit: int = None, offset: int = None, fields: Sequence[AnimeField] = None, nsfw: bool = None) -> dict:
    return await _get('anime',
                      q=query,
                      limit=limit,
                      offset=offset,
                      nsfw=nsfw,
                      fields=','.join(fields) if fields else None)


async def get_anime_details(id: int, /, fields: Sequence[AnimeField] = None, nsfw: bool = None) -> dict:
    return await _get(f'anime/{id}',
                      nsfw=nsfw,
                      fields=','.join(fields) if fields else None)
