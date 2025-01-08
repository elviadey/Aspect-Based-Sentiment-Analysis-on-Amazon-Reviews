import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor

reviewlist = []

def get_soup(url):
    r = requests.get('http://localhost:8050/render.html', params={'url': url, 'wait': 2})
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def get_reviews(soup, product_name):
    reviews = soup.find_all('div', {'data-hook': 'review'})
    for item in reviews:
        review = {
            'product': product_name,
            'title': re.sub(r'\d+\.\d+', '', item.find('a', {'data-hook': 'review-title'}).text.replace('out of 5 stars', '')).strip(),
            'rating':  float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()),
            'body': item.find('span', {'data-hook': 'review-body'}).text.strip(),
        }
        reviewlist.append(review)

def scrape_reviews(url):
    product_name = None
    for x in range(1, 20):  # Assuming no more than 9999 pages
        soup = get_soup(url.format(x=x))
        if x == 1:
            product_name = soup.title.text.replace('Amazon.in:Customer reviews: ', '').strip()
        print(f'Getting page {x} for {product_name}')
        get_reviews(soup, product_name)
        if soup.find('li', {'class': 'a-disabled a-last'}):
            break

# List of URLs to scrape
urls = [
    "https://www.amazon.in/Moisturizer-Non-Greasy-Vitamin-Instant-Hydration/product-reviews/B00E96N6O8/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber={x}",
    "https://www.amazon.in/NIVEA-Bath-Lemon-Shower-250ml/product-reviews/B00G6IXG7Y/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber={x}",
    "https://www.amazon.in/NIVEA-Protect-Moisture-125ml-Sunscreen/product-reviews/B00E96MU5E/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber={x}"
    ]

# Scrape reviews for each URL using ThreadPoolExecutor for parallel execution
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(scrape_reviews, urls)

# Convert review list to DataFrame and save to Excel
df = pd.DataFrame(reviewlist)
df.to_excel('product_reviews8.xlsx', index=False)
print('Fin.')
