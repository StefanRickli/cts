from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from time import sleep

wait_time = 5

# earliest : 200821
from_year = 2009
from_week = 3
to_year = 2018
to_week = 30

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(url, resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(url, resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    
    if resp.url != url:
        print('{} did not exist. Skipping...'.format(url))
        return False
    
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_chartnumbers(from_year, from_week, to_year, to_week):
    assert(from_year >= 2008 and from_year <= 2018)
    assert(to_year >= 2008 and to_year <= 2018)
    assert(from_week >= 1 and from_week <= 53)
    assert(to_week >= 1 and to_week <= 53)
    
    assert(from_year <= to_year)
    if from_year == to_year:
        assert(from_week <= to_week)
    
    chartnumbers = []
    for yyyy in range(from_year, to_year + 1):
        if yyyy == from_year:
            from_week_current = from_week
        else:
            from_week_current = 1

        if yyyy == to_year:
            to_week_current = to_week
        else:
            to_week_current = 53

        for ww in range(from_week_current, to_week_current + 1):
            chartnumbers.append('{:04}{:02}'.format(yyyy, ww))

    return chartnumbers


if __name__ == '__main__':
    chartnumbers = get_chartnumbers(from_year, from_week, to_year, to_week)
    base_url = 'https://www.tanzmusik-online.de/charts/{}'    

    for i in range(len(chartnumbers)):
        url = base_url.format(chartnumbers[i])

        print('{}, {}: {}'.format(i, chartnumbers[i], url))

        response = simple_get(url)
        if response is not None:
            filename = chartnumbers[i] + '.html'
            with open(filename, 'wb') as f:
                f.write(response)
                print('Successfully wrote to {}'.format(filename))

        print('Waiting for {}s...'.format(wait_time))
        sleep(wait_time)
