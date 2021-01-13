# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 10:51:11 2021

@author: Wolke
"""

# Import packages needed
import pandas as pd
import numpy as np
import re

# url for where the game data is being hosted
url = "https://raw.github.com/pmwolke/steam_store/main/all_steam_games.csv"

# Create a dataframe from the csv file
df = pd.read_csv(url, index_col=0)

# Initialize lists for genres and for rows where data type is not correct
all_genres = []
something_wrong = []

# Loop through our genres data to get a list of all genres found in the data set
for index in df.index:
    
    # If statement in case their is an error in the data type
    if type(df["genres"][index]) == str:
        
        # The genres data imports as a string, so we need to remove brackets, commas, etc.
        genre_list = re.sub(r"[,]", "", df["genres"][index])
        genre_list = re.sub(r"[']", "", genre_list)
        genre_list = re.sub(r"[\[]", "", genre_list)
        genre_list = re.sub(r"[\]]", "", genre_list)
        
        # Create a list by splitting the newly created string
        game_genres = genre_list.split()
        
        # Go through the list of genres for game at this index and add them to master list of genres if not already present
        for genre in game_genres:
            if genre not in all_genres:
                all_genres.append(genre)
    # Keep track of errors
    else:
        something_wrong.append(index)

# Save list of id's that gave an error
np_something_wrong = np.array(something_wrong)
np.savetxt("something_wrong.csv", np_something_wrong, delimiter=",")

# Taking the master list of genres, we create a column for each genre
for genre in all_genres:
    
    # Initialize list for all games with this genre
    genre_exists = []
    
    # If game is of this genre, set to 1, otherwise set to 0
    for index in df.index:
        if genre in df["genres"][index]:
            genre_exists.append(1)
        else:
            genre_exists.append(0)
    
    # Add column to dataframe with column name as the genre name, and the list of 1's and 0's as the new data points for each row
    df[genre] = genre_exists

# Save new dataframe to a csv
df.to_csv("all_steam_games_cleaned_genres.csv")
