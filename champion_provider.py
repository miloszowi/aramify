import requests
import random

class ChampionProvider:
    pool = {}
    champions = {}

    def __init__(self, exclude_tags):
        self.champions = requests.get('https://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json').json()['data']

        self.pool = {
            k: {**v, 'image': {**v['image'], 'full': v['image']['full'].replace('FiddleSticks', 'Fiddlesticks')}}
            for k, v in self.champions.items()
            if not any(tag in exclude_tags for tag in v['tags'])
        }

    def draw(self, amount) -> dict:
        try:
            draw = dict(random.sample(list(self.pool.items()), amount))
        except ValueError:
            # no more items to draw as pool is empty
            return {}

        for key in draw.keys():
            self.pool.pop(key)

        return draw

    def tags(self) -> list:
        tags_list = []

        for champion in self.champions.values():
            tags_list.extend(champion.get('tags', []))

        unique_tags = list(set(tags_list))

        return unique_tags
