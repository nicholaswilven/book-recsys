import pandas as pd
import numpy as np

def load_books():
    """Load books dataframe and apply preprocessing
    Steps:
        Remove Image-URL-S and Image-URL-M column
        Rename columns into lowercase and shorter name
        Fix error from bad csv seperator
        Remove books with year<1901 or year>2023
        """
    books = pd.read_csv("data/Books.csv")

    books.drop(['Image-URL-S', 'Image-URL-M'], axis= 1, inplace= True)

    books.rename(columns={'ISBN':'isbn',
                          'Book-Title':'title',
                          'Book-Author':'author',
                          'Year-Of-Publication':'year',
                          'Publisher':'pub'
                          },inplace=True)

    # Attempt to find the error in column 3 (from warning)
    books['error'] = books['year'].apply(lambda x: not str(x).isnumeric())

    L  = list(books[books['error']].index)
    for l in L:
        books.loc[l,'pub'] = books.loc[l,'year']
        books.loc[l,'year'] = books.loc[l,'author']
        books.loc[l,'author'] = books.loc[l,'title'].split('\\";')[1].replace('"','')
        books.loc[l,'title'] = books.loc[l,'title'].split('\\";')[0]\

    books['year'] = pd.to_numeric(books['year'])
    books = books[(books['year']>1900) & (books['year']<2024)]
    return books

def load_ratings():
    """Load ratings dataframe and apply preprocessing
    Steps:
        Rename columns into lowercase and shorter name
        Remove rows with rating=0
        """
    ratings = pd.read_csv("data/Ratings.csv")
    
    ratings.rename(columns={'ISBN':'isbn',
                      'Book-Rating':'rating',
                      'User-ID':'user_id'
                      },inplace=True)
    
    ratings = ratings[ratings['rating']>0]
    return ratings

def load_users():
    """Load ratings dataframe and apply preprocessing
    Steps:
        Rename columns into lowercase and shorter name
        Remove age values if >90 or <10
        """
    users = pd.read_csv("data/Users.csv")

    users.rename(columns={'User-ID':'user_id',
                          'Location':'location',
                          'Age':'age'
                          },inplace=True)

    # users['country'] = users['location'].apply(lambda x: x.split(', ')[-1])

    # Limit age to reasonable interval
    users['age'] = users['age'].apply(lambda x: np.nan if (x>90 or x<10) else x)
    return users