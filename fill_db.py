import asyncio
import asyncpg
import json
import sys

sys.path += '.'

from dbUtils import Table
import generator


def load_json_entity_description():
    with open('sst.json') as js_f:
        return json.load(js_f)


async def fill_sample_table(pg_pool):
    entity_description = load_json_entity_description()

    entity_table = Table(entity_description)

    await asyncio.sleep(1*60)  # mock request
    requested_data = [generator.generate_row(entity_description) for _ in range(10000)]

    async with pg_pool.acquire() as con_insert:
        return len(await entity_table.insert(connection=con_insert, data=requested_data))


async def run():
    async with asyncpg.create_pool(host='docker-postgresql', min_size=3, max_size=3, user='sample', password='sample',
                                   command_timeout=60) as pg_pool:
        tasks = []
        iterator = 0

        for iter_daterange in range(1, 33):
            if iterator > 10:
                iterator = 0
                await asyncio.gather(*tasks, return_exceptions=True)

                await asyncio.sleep(10 * 60, loop=loop)
                tasks = []

            tasks.append(
                asyncio.ensure_future(fill_sample_table(
                    pg_pool=pg_pool
                ))
            )
            iterator += 1
        if iterator > 0:
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
