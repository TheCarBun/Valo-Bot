import aiohttp

async def acc_info(name:str, tag:str):    
    async with aiohttp.ClientSession() as session:
        headers = {
            'accept': 'application/json'
        }
        response = await session.get(f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}', headers = headers)
        account_info = await response.json()
    return account_info

async def mmr_info_v1(puuid):
    async with aiohttp.ClientSession() as session:
        headers = {
            'accept': 'application/json'
        }
        response = await session.get(f'https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr/ap/{puuid}', headers = headers)
        mmr_info = await response.json()
    return mmr_info

async def mmr_info_v2(puuid):
    async with aiohttp.ClientSession() as session:
        headers = {
            'accept': 'application/json'
        }
        response = await session.get(f'https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/ap/{puuid}', headers = headers)
        mmr_info = await response.json()
    return mmr_info

async def featured_store():
    async with aiohttp.ClientSession() as session:
        headers = {
            'accept': 'application/json'
        }
        response = await session.get(f'https://api.henrikdev.xyz/valorant/v2/store-featured', headers = headers)
        store_info = await response.json()
    return store_info
