from bs4 import BeautifulSoup
import requests


def get_url_params(url: str = None) -> dict:
    try:
        response = requests.get(url[0]['name'])
        if response.status_code != 200:
            return None, response.status_code
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title').text[:255] if soup.find('title') else ''
            h1 = soup.find('h1').text[:255] if soup.find('h1') else ''
            description = soup.find(
                'meta', attrs={'name': 'description'})['content'][:255] \
                if soup.find('meta', attrs={'name': 'description'}) else ''
            return {'title': title, 'h1': h1, 'description': description}
    except Exception as e:
        return None, {'error': e}
