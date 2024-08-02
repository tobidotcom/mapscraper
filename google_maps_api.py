import aiohttp
import logging

async def fetch_businesses_for_postal_code(search_query, postal_code, google_maps_api_key, session):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_query}+in+{postal_code}&key={google_maps_api_key}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = await response.json()
            logging.debug(f"API Response for postal code {postal_code}: {data}")
            return data.get('results', [])
    except aiohttp.ClientError as e:
        logging.error(f"Client error for postal code {postal_code}: {e}")
        return []
    except Exception as e:
        logging.error(f"Error fetching businesses for postal code {postal_code}: {e}")
        return []
