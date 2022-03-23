import asyncio
from pathlib import Path

import graphviz
import httpx

from related_anime import AnimeEntry, find_anime, get_related_anime


async def download(anime: AnimeEntry):
    filename = Path(f"cache/anime/{anime.id}.jpg")
    filename.parent.mkdir(parents=True, exist_ok=True)
    if filename.is_file():
        return anime.id, filename

    async with httpx.AsyncClient() as client:
        with open(filename, 'wb') as f:
            async for chunk in (await client.get(anime.image_url)).aiter_bytes():
                f.write(chunk)

    return anime.id, filename


async def main():
    def log_progress(jobs_processed, jobs_started):
        print(f"\rProgress: {jobs_processed} / {jobs_started}", end="")

    related_anime, anime_relations = await get_related_anime(await find_anime(), log_progress)
    print()

    if not related_anime:
        return

    print(f"Found a total of {len(related_anime)} related anime.")

    anime_images = dict(await asyncio.gather(*[download(anime) for anime in related_anime.values() if anime.image_url]))

    node_font = 'bahnschrift'
    edge_font = 'Segoe UI'

    graph = graphviz.Digraph("anime-graph")

    for anime_id, anime in related_anime.items():
        image = f"""<TR>
            <TD COLSPAN="2"><IMG SCALE="TRUE" SRC={graphviz.quoting.quote(image_url.as_posix())}/></TD>
        </TR>""" if (image_url := anime_images.get(anime_id)) else ""

        graph.node(str(anime_id),
                   shape="plain",
                   label=f"""<
                 <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" HREF="https://myanimelist.net/anime/{anime_id}" TOOLTIP="{anime_id}">
                    <TR>
                        <TD COLSPAN="2"><![CDATA[{anime.title}]]></TD>
                    </TR>
                    <TR>
                        <TD>{anime.num_episodes or '?'} episodes</TD>
                        <TD>{anime.start_date}</TD>
                    </TR>
                    {image}
                 </TABLE>>""",
                   fontname=node_font)

    skippable = {
        ('sequel', 'prequel'),
        ('side_story', 'parent_story'),
        ('spin_off', 'parent_story'),
        ('summary', 'full_story'),
        ('summary', 'parent_story'),
        ('parent_story', 'other'),
        ('side_story', 'other'),
    }

    def can_skip(forward_relation, from_id, to_id):
        return (backward := anime_relations.get((to_id, from_id))) is not None and (backward.relation_type, forward_relation) in skippable

    for anime_relation in anime_relations.values():
        from_id = anime_relation.from_id
        to_id = anime_relation.to_id

        if can_skip(anime_relation.relation_type, from_id, to_id):
            continue

        if (undirected := (backward := anime_relations.get((to_id, from_id))) and anime_relation.relation_type == backward.relation_type):
            if from_id > to_id:
                continue

        graph.edge(str(from_id), str(to_id),
                   label=None if anime_relation.relation_type == 'sequel' else anime_relation.relation_type_formatted,
                   dir='none' if undirected else None,
                   fontname=edge_font,
                   penwidth='5' if anime_relation.relation_type == 'sequel' else '1')

    graph.render(format='svg', view=True, cleanup=True)


if __name__ == '__main__':
    asyncio.run(main())
