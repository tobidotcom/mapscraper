import aiohttp

async def fetch_businesses_for_postal_code(search_query, postal_code, google_maps_api_key, session):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_query}+in+{postal_code}&key={google_maps_api_key}"
    async with session.get(url) as response:
        data = await response.json()
        return data.get('results', [])

