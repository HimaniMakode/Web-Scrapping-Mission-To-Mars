import os
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
from selenium import webdriver
from splinter.exceptions import ElementDoesNotExist
import time
from time import sleep


def scrape_all():
    executable_path = {"executable_path": 'chromedriver'}
    browser = Browser("chrome", **executable_path,
                      headless=True)  # add headless=True to avoid the window pop up showing the scraping

    news_title, news_paragraph = mars_news(browser)
    featured_image_url = feature_image(browser)
    mars_weather = mars_twitter(browser)
    mars_facts_data = mars_facts(browser)
    mars_hemisphere_image_urls = mars_hemisphere_images(browser)

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": feature_image(browser),
        "mars_weather": mars_twitter(browser),
        "mars_facts_data": mars_facts(browser),
        "mars_hemisphere_images": mars_hemisphere_images(browser)
    }

    return data


def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    html = browser.html
    soup = bs(html, 'html.parser')
    try:
        news_title = soup.find('div', class_="content_title").get_text()
        news_paragraph = soup.find('div', class_="article_teaser_body").get_text()
    except:
        return None, None

    return news_title, news_paragraph


def feature_image(browser):
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    browser.is_element_present_by_text('more info   ', wait_time=2)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    jpl_html = browser.html
    jpl_soup = bs(jpl_html, "lxml")
    try:
        img_url_rel = jpl_soup.select_one('figure.lede a img').get("src")
        featured_image_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    except:
        return None, None

    return featured_image_url


def mars_twitter(browser):
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(twitter_url)
    twitter_html = browser.html
    twitter_soup = bs(twitter_html, "lxml")
    try:
        latest_weather = twitter_soup.find('div', class_='js-tweet-text-container')
        mars_weather_first = latest_weather.find('p', class_='js-tweet-text').text
        latest_weather_all = twitter_soup.find_all('div', class_='js-tweet-text-container')

        weather_list = []
        for weather in latest_weather_all:
            mars_weather = weather.find('p', class_='js-tweet-text').text
            weather_list.append(mars_weather)

        mars_weather = [x for x in weather_list if 'InSight' in x][0]

    except:
        return None, None

    return mars_weather


def mars_facts(browser):
    mars_facts_url = 'https://space-facts.com/mars/'
    browser.visit(mars_facts_url)
    mars_facts_html = browser.html
    mars_facts_soup = bs(mars_facts_html, "lxml")

    try:
        mars_facts_tables = pd.read_html(mars_facts_url)
        mars_facts_tables_df = mars_facts_tables[1]
        mars_facts_tables_df.columns = ['Description', 'Value']
        mars_facts_tables_df.set_index('Description', inplace=True)
        mars_facts_data = mars_facts_tables_df.to_html()
    except:
        return None, None

    return mars_facts_data


def mars_hemisphere_images(browser):
    mars_hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemisphere_url)
    mars_hemisphere_html = browser.html
    mars_hemisphere_soup = bs(mars_hemisphere_html, 'lxml')
    try:
        list_of_mars_hemispheres = mars_hemisphere_soup.find_all('div', class_='item')

        mars_hemisphere_image_urls = []
        base_url = 'https://astrogeology.usgs.gov'

        for image in list_of_mars_hemispheres:
            hemi_dict = {}
            mars_image_hemi = image.find('a', class_='itemLink product-item')
            link = base_url + mars_image_hemi['href']
            browser.visit(link)
            time.sleep(1)
            mars_hemisphere_html_loop = browser.html
            mars_hemisphere_html_loop_soup = bs(mars_hemisphere_html_loop, 'lxml')
            image_title = mars_hemisphere_html_loop_soup.find('div', class_='content').find('h2', class_='title').text
            hemi_dict['title'] = image_title
            image_link = mars_hemisphere_html_loop_soup.find('div', class_='downloads').find('a')['href']
            hemi_dict['img_url'] = image_link
            mars_hemisphere_image_urls.append(hemi_dict)

    except:
        return None, None
    return mars_hemisphere_image_urls

    browser.quit()