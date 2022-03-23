import asyncio
import math
import sys
from dataclasses import dataclass
from typing import Callable, Optional

import mal


class AnimeID(int):
    pass


@dataclass
class AnimeEntry:
    id: AnimeID
    title: str
    start_date: str
    num_episodes: Optional[int]
    image_url: Optional[str]


@dataclass
class AnimeRelation:
    from_id: AnimeID
    to_id: AnimeID
    relation_type: str
    relation_type_formatted: str


class RelatedAnime(dict[AnimeID, AnimeEntry]):
    pass


class AnimeRelations(dict[tuple[AnimeID, AnimeID], AnimeRelation]):
    pass


async def get_related_anime(anime_id: int, progress: Callable[[int, int], None] = None) -> tuple[RelatedAnime, AnimeRelations]:
    related_anime = RelatedAnime()
    anime_relations = AnimeRelations()

    jobs_processed = 0
    jobs_started = 0

    if progress is None:
        def update_progress():
            pass
    else:
        def update_progress():
            progress(jobs_processed, jobs_started)

    async def get_anime_details_log(id: AnimeID):
        nonlocal jobs_processed, jobs_started
        jobs_started += 1
        update_progress()
        response = await mal.get_anime_details(id, fields=['related_anime', 'start_date', 'num_episodes', 'main_picture'])
        jobs_processed += 1
        update_progress()
        return response

    anime_ids_to_process = [anime_id]
    while anime_ids_to_process:
        next_to_process = [
            get_anime_details_log(anime_id) for anime_id in anime_ids_to_process
        ]
        additional_relations = set()
        for current_anime in await asyncio.gather(*next_to_process):
            main_picture = current_anime.get('main_picture')
            related_anime[current_anime['id']] = AnimeEntry(
                id=current_anime['id'],
                title=current_anime['title'],
                start_date=current_anime.get('start_date', '????-??-??'),
                num_episodes=current_anime.get('num_episodes'),
                image_url=main_picture.get('medium') if main_picture else None
            )

            anime_relations.update((
                (current_anime['id'], current_related_anime['node']['id']),
                AnimeRelation(
                    from_id=current_anime['id'],
                    to_id=current_related_anime['node']['id'],
                    relation_type=current_related_anime['relation_type'],
                    relation_type_formatted=current_related_anime['relation_type_formatted']
                )
            ) for current_related_anime in current_anime['related_anime'])

            additional_relations |= {current_related_anime['node']['id'] for current_related_anime
                                     in current_anime['related_anime']}

        anime_ids_to_process = [
            relation for relation
            in additional_relations
            if relation not in related_anime
        ]

    return related_anime, anime_relations


async def find_anime():
    try:
        anime_id = int(sys.argv[1])
        print(f"Scanning relations for {anime_id}")
        return anime_id
    except ValueError:
        anime_query = " ".join(sys.argv[1:])

        if (found_anime_list := (await mal.list_anime(anime_query, limit=1, nsfw=True)).get('data', None)) is None:
            print("No anime found.")
            return

        found_anime = found_anime_list[0]['node']
        print(f"Scanning relations for {found_anime['title']}")
        return found_anime['id']



async def main():
    def log_progress(jobs_processed, jobs_started):
        print(f"\rProgress: {jobs_processed} / {jobs_started}", end="")

    related_anime, anime_relations = await get_related_anime(await find_anime(), log_progress)
    print()

    if not related_anime:
        return

    sorted_anime = sorted(related_anime.values(),
                          key=lambda entry: entry.start_date)
    max_width = max(int(math.log10(anime.id)) +
                    1 for anime in sorted_anime)
    for anime in sorted_anime:
        print(f"[{anime.id:>{max_width}}] {anime.start_date:<10} - {anime.title}")

    print(f"Found a total of {len(sorted_anime)} related anime.")


if __name__ == '__main__':
    asyncio.run(main())
