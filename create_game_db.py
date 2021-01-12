# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 10:50:18 2021

@author: Wolke
"""

# Import libraries
import urllib
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
import numpy as np

# We will define a function that will take a BeautifulSoup object and return a dictionary with relevant data points
def scrape_html_for_data(soup):
    
    """Takes a BeautifulSoup object and returns a dictionary with data fields for games on the Steam Store"""

    # Set dictionaries for where we can find all game data within html - genres, title, datte, developer, publisher, price, etc.
    dict_for_genres = {'class': 'app_tag'}
    dict_for_name = {"class": "apphub_AppName"}
    dict_for_date = {"class":"date"}
    dict_for_developer = {"class":"summary column", "id":"developers_list"}
    dict_for_positive_reviews = {"type":"hidden", "id":"review_summary_num_positive_reviews"}
    dict_for_all_reviews = {"type":"hidden", "id":"review_summary_num_reviews"}
    dict_for_currency = {"itemprop":"priceCurrency"}
    dict_for_price = {"itemprop":"price"}
    dict_for_discount = {"class":"game_area_purchase_game_wrapper", "class":"game_purchase_action", "class":"discount_original_price"}

    # Get a list of genres
    genres = []
    for link in soup.find_all(attrs=dict_for_genres):
        genre = link.text
        genre = re.sub(r"[\n\t\s]*", "", genre) # We want to remove blank characters
        genres.append(genre)
    # Most games have a "+" character at the end of the list within the html, we want to remove it if it is there
    if "+" in genres:
        genres.remove("+")

    # Get the name (title) of the game
    if soup.find(attrs=dict_for_name) == None: # If title isn't on the page, we need to declare None
        game_title = "NaN"
    else:
        game_title = soup.find(attrs=dict_for_name).text

    # Get the release date
    if soup.find(attrs=dict_for_date) == None: # If release date isn't on the page, we need to declare None
        release_date = "NaN"
    else:
        release_date = soup.find(attrs=dict_for_date).text
        # Sometimtes the date format isn't in this form, so we need an exception clause so we don't get errors
        try:
            release_date = datetime.datetime.strptime(release_date, '%b %d, %Y')
        except:
            release_date = "NaN"

    # Get the developer name
    if soup.find(attrs=dict_for_developer) == None: # If developer name isn't on the page, we need to declare None
        developer = "NaN"
    else:
        developer = soup.find(attrs=dict_for_developer).a.text
    
    # Get the publisher
    text_to_list = [text for text in soup.stripped_strings] # Create a list of all text within soup
    # From reading the html, we know that the publisher name comes after the text "Publisher:"
    try:
        publisher_index = text_to_list.index("Publisher:") + 1
        publisher = text_to_list[publisher_index]
    except ValueError:
        publisher = "NaN"
        
    # Get positive review count
    if soup.find(attrs=dict_for_positive_reviews) == None: # Some games have no reviews, so we need to declare None
        positive_reviews = "NaN"
        all_reviews = "NaN"
    else:
        positive_reviews_location = soup.find(attrs=dict_for_positive_reviews)
        positive_reviews = positive_reviews_location["value"]
        positive_reviews = int(positive_reviews) # Convert to int
        # Get total reviews count
        all_reviews_location = soup.find(attrs=dict_for_all_reviews)
        all_reviews = all_reviews_location["value"]
        all_reviews = int(all_reviews) # Convert to int

    # Check to see if a price exists as some games are free or can't be purchased
    if soup.find(attrs=dict_for_currency) == None:
        currency = "NaN"
    else:
        # Get the currency, so we can make sure comparisons in price are accurate
        currency_location = soup.find(attrs=dict_for_currency)
        currency = currency_location["content"]
    
    # Get the price for the game
    if soup.find(attrs=dict_for_price) == None:
        price = "NaN"
    else:
        price_location = soup.find(attrs=dict_for_price)
        price = price_location["content"]
        price = float(price) # Convert to float
    
    # Get the non-discount price for a game
    if soup.find(attrs=dict_for_discount) == None:
        discount_original_price = "NaN"
    else:
        search_for_discount = soup.find(attrs=dict_for_discount)
        # If a discount is available, we look to see what the original price is
        if search_for_discount != None:
            discount_location = soup.find(attrs=dict_for_discount)
            discount_original_price = discount_location.text
            discount_original_price = re.sub(r"[$]", "", discount_original_price) # We want to remove the '$' so we can convert to float
            # There are ocassional discrepancies that force us to check that the string can be converted to float
            try:
                discount_original_price = float(discount_original_price)
            except:
                discount_original_price = "NaN"
        # If no discount is there, then the original price is the current price on the store page
        else:
            discount_original_price = price
    
    # Return a dictionary of all data points we have found within the soup
    return_dictionary = {"game_title":game_title,
                        "developer": developer,
                        "publisher": publisher,
                        "release_date": release_date,
                        "positive_reviews": positive_reviews,
                        "all_reviews": all_reviews,
                        "currency": currency,
                        "price": price,
                        "original_price": discount_original_price,
                        "genres": genres}
    
    return return_dictionary

# Make a simple function to request html and turn into soup
def make_steam_soup(app_id):
    
    """Given an app_id on the Steam Store, return clean HTML in form of BeautifulSoup object"""
    
    # Create url based on app_id
    url = "https://store.steampowered.com/app/" + str(app_id)
    # We need a try statement as there are at times issues with making a url request
    try:
        with urllib.request.urlopen(url) as response: # A with statement ensures we close request
            html = response.read()
        soup = BeautifulSoup(html, features="lxml") # Convery html into BeautifulSoup
    # Return a specific string if we have an error requesting url
    except urllib.error.HTTPError:
        soup = "HTTPError"
    
    # Return the html as a soup object
    return soup

# Need to create a function that will turn the dictionary from scrape_html_for_data into a pandas dataframe
def game_dict_to_df(dictionary, df_old, app_id):
    
    """Given a dictionary and pandas dataframe, this function will append the values from the dictionary
    to the given dataframe and then return a new dataframe"""
    
    # Define values and keys from dictionary
    values = dictionary.values()
    columns = dictionary.keys()
    
    # Create a temporary dataframe from data in dictionary 
    df_from_dict = pd.DataFrame([values], columns=columns, index=[app_id])
    
    # Append data from dictionary to the given dataframe
    df_new = df_old.append(df_from_dict)
    
    # Return a new dataframe object
    return df_new

# Define column names based on data we are scrapping from Steam
column_names = ["game_title",
                "developer",
                "publisher",
                "release_date",
                "positive_reviews",
                "all_reviews",
                "currency",
                "price",
                "original_price",
                "genres"]

# Create a new dataframe to host data
game_data_df = pd.DataFrame(columns=column_names)

# Create a new csv file so we can save this data in a more permanent format
game_data_df.to_csv("all_steam_games.csv")

# At the time of this code, app ids on Steam went up to roughly 1,500,000 which is reflected in app_id_max
app_id_max = 1500000

# This number will reflect how often we save this data to our csv
app_id_size = 10000

# We want to keep track of app_ids that have an HTTPError, so we can try them on a later date
app_ids_to_retry = []

# Start time to keep track of progress as it will take some time to scrape all this information
start_time = datetime.datetime.now()
print("Starting at: ", start_time)

# Our outerloop is mainly here so we can track and save progress at regular intervals
for k in range(0, app_id_max, app_id_size):
    
    # A list of app id's so we can append them to the csv file on each iteration of k
    app_id=[]
    
    # This inner loop is were the data scrapping happens
    for i in range(k, k+app_id_size, 10): #We go by 10's as we noticed most non-DLC games are a multiple of 10
        # Make url request can convert to BeautifulSoup
        game_soup = make_steam_soup(i)
        
        # Check if there was an error, and add to id's to try again if there was
        if game_soup == "HTTPError":
            app_ids_to_retry.append(i)
        else:
            # If an app id does not exist on Steam, it redirects to the home page
            if game_soup.title.string != "Welcome to Steam": # The home page always has title "Welcome to Steam"
                game_data = scrape_html_for_data(game_soup) # Scrape html for data we want
                game_data_df = game_dict_to_df(game_data, game_data_df, i) # Convert data we want from dictionary to dataframe
                app_id.append(i) # Add id to list so we know it was an id to an actual game on steam
            
    # Add data from this group of app id's to the csv file for long term storage
    game_data_df.loc[app_id].to_csv("all_steam_games.csv", mode="a", header=False)\
    
    # Print out some information in the terminal so we can keep track of progress
    print("Completed " + str(k) + " - " + str(k + app_id_size) + " at: ", datetime.datetime.now())
    print("Time since task started: ", datetime.datetime.now() - start_time)

# Final message so we know the process is complete
print("Data scrapping complete at: ", datetime.datetime.now())
print("Time to complete: ", datetime.datetime.now() - start_time)

# Save app id's that generated an HTTP error so we can test them later
np_app_ids_to_retry = np.array(app_ids_to_retry)
np.savetxt("app_ids_to_retry.csv", np_app_ids_to_retry, delimiter=",")
    
