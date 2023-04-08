import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz

def get_u_ratings(book_ratings):
    """ Groupby ratings dataframe to get rating mean and count for each book
    main purpose: increase traditional filtering efficiency
    Args:
      ratings: ratings dataframe
    Output:
      u_ratings: rating mean and count dataframe (title as index)
    """
    u_ratings = pd.concat([book_ratings.groupby('title').rating.mean(), book_ratings.groupby('title').rating.count()], axis=1)
    u_ratings.columns = ['rating', 'count']
    u_ratings.reset_index(inplace=True)
    u_ratings.set_index('title',inplace=True)
    return u_ratings

def rec_by_pop(u_ratings, books, ban_list=[]):
    """ Recommend books by user with no data
    main purpose: for new users and additional recommendation
    Args:
      u_ratings: rating mean and count dataframe
      books: books dataframe
      ban_list : remove title from list of recommendation (already read book)
    Output:
      dataframe of top_10 most popular books (score: rating>0 count)
    """
    p_ratings = u_ratings[~u_ratings.index.isin(ban_list)]
    L_final_title = p_ratings['count'].sort_values(ascending=False).head(10)
    return books.loc[books['title'].isin(L_final_title.index)].drop_duplicates('title')

def rec_by_age(age, users, books, book_ratings, ban_list=[]):
    """ Recommend books by user with similar age data,
    main purpose: recommend for users with only age data
    Args: 
      age: age of user
      users: users dataframe
      book_ratings : merge of books and ratings dataframe
      ban_list : remove title from list of recommendation (already read book)
    Output:
      dataframe of top 10 scored books in age group . Method: age group: age gap < 3,
    score = ratings*score (for balance between quality and quantity of ratings)
    """
    # Find users with similar age
    L_sim_age_users = users[(users['age']>age-3) & (users['age']<age+3)]['user_id']
    L_books = book_ratings[book_ratings['user_id'].isin(L_sim_age_users)]
    
    # Find localized ratings for the age group
    age_ratings = get_u_ratings(L_books)
    
    # Pick top 10 scored book as recommendation
    p_ratings = age_ratings[~age_ratings.index.isin(ban_list)]
    p_ratings['rating x count'] = p_ratings['count']*p_ratings['rating']
    L_final_title = p_ratings['rating x count'].sort_values(ascending=False).head(10)
    return books.loc[books['title'].isin(L_final_title.index)].drop_duplicates('title')

def rec_by_title(title, books, book_ratings, ban_list=[]):
    """ Recommend books by similar title,
    main purpose: recommend for books when collaborative filtering fails
    Args: 
      title : book title to search
      books : books dataframe
      book_ratings : merge of books and ratings dataframe
      ban_list : remove title from list of recommendation (already read book)
    Output:
      dataframe of top 10 books with similar title, scored using fuzzywuzzy token set ratio
    """
    z = book_ratings.groupby('title').rating.count()>10
    L_title = z[z].reset_index()
    L_title['title_sim_score'] = L_title['title'].apply(lambda x: fuzz.token_set_ratio(title, x))
    L_final_title = L_title[~L_title['title'].isin(ban_list)].sort_values('title_sim_score',ascending=False).head(10)
    return books.loc[books['title'].isin(L_final_title.title)].drop_duplicates('title')
