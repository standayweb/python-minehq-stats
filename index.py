from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from bs4 import BeautifulSoup
import cfscrape


def player_stats(request):
    # Concat url string to use variable from route.
    url = 'https://www.minehq.com/players/%(name)s' % request.matchdict

    # Fetch html from the url and convert it into page
    # object with methods we can use to get data and such.
    scraper = cfscrape.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    if soup.find('h2') is not None and soup.find('h2').text.strip() == 'Not Found (404)':
        # Send error tell.
        data = {
            'name': None,
            'lastSeen': None,
            'joinedDate': None,
            'error': 'The player you entered doesn\'t exist on minehq.',
        }
    else:
        # Pull out data and store them it an dict.
        data = {
            'name': soup.find(id='username').text.strip(),
            'lastSeen': soup.find(id='profile_header').find_all('p')[0].text.strip(),
            'joinedDate': soup.find(id='profile_header').find_all('p')[1].text.strip(),
            'error': None,
        }

    # Return the dict in the http response.
    return Response(json=data)

if __name__ == '__main__':
    config = Configurator()
    config.add_route('player', '/player/{name}')
    config.add_view(player_stats, route_name='player')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
