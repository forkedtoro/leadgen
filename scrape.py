#! /usr/bin/python

import settings
import os
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from yelp.errors import InvalidParameter

all_categories = {}
for category in settings.CATEGORIES:
    all_categories[category] = 0

def get_category(mcategory):
    auth = Oauth1Authenticator(
        consumer_key=settings.CONSUMER_KEY,
        consumer_secret=settings.CONSUMER_SECRET,
        token=settings.TOKEN,
        token_secret=settings.TOKEN_SECRET
    )

    client = Client(auth)
    offset = 0

    while True:
        params = {
            'category_filter': mcategory,
            'offset': offset
        }
        try:
            response = None
            response = client.search(settings.CITY, **params)
        except InvalidParameter:
            all_categories[mcategory] = -1
            break
        print '{} {} {}'.format(params, len(response.businesses), response.total)
        for business in response.businesses:
            try:
                categories = [category.alias for category in business.categories]
            except TypeError:
                continue
            if settings.RECURSE_CATEGORIES:
                for category in categories:
                    if category.lower().replace(" ","") not in all_categories:
                        all_categories[category.lower().replace(" ","")] = 0
            with open('output/businessdata.csv', 'a') as outfile:
                try:
                    outfile.write(
                        '"{0}"|"{1}"|"{2}"|"{3}"|"{4}"|"{5}"|"{6}"|"{7}"|"{8}"|"{9}"|"{10}"\n'.format(
                            business.id,
                            business.name,
                            ', '.join(sorted(categories)),
                            business.review_count,
                            business.rating,
                            business.url,
                            business.phone,
                            ', '.join(business.location.address),
                            business.location.city,
                            business.location.state_code,
                            business.location.postal_code
                        )
                    )
                except UnicodeEncodeError:
                    pass
        offset += 20
        if len(response.businesses) < 20:
            all_categories[mcategory] = 1
            break

done = False
while not done:
    for category in all_categories:
        if all_categories[category] == 0:
            get_category(category)
            break
    print category
    done = True
    for category in all_categories:
        if all_categories[category] == 0:
            done = False

os.system('sort output/businessdata.csv | uniq > output/businessdata_uniq.csv')
