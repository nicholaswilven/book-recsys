import pandas as pd
from traditional_filtering import *
from collaborative_filtering import *
from load_data import *

books = load_books()
ratings = load_ratings()
users = load_users()

book_ratings = pd.merge(ratings, books, on='isbn')
u_ratings = get_u_ratings(book_ratings)
pt, item_similarity = user_based_cf(book_ratings)

def generate_recommendation(user_id = None, title = None, no_cf = False):
    if user_id != None:   # When given user_id, will use user_id for giving recommendation
        if user_id not in users['user_id']:
            raise ValueError("No existing user with this id. Please register first")
        try: # Collaborative filtering will fail if user have no ratings for famous books
            if no_cf:
                raise Exception('Request asked for no collaborative filtering')
            rec_df = recommend_book_to_user(user_id, pt, item_similarity, books, book_ratings)
        except: # Traditional filtering using age if available or universal rating
            age = users[users['user_id']==user_id]['age'].iloc[0]
            if np.isnan(age):
                rec_df = rec_by_pop(u_ratings, books)
            else:
                rec_df = rec_by_age(age, users, books, book_ratings)
    else:    
        try: # Collaborative filtering will fail if book is not a famous books
            if no_cf:
                raise Exception('Request asked for no collaborative filtering')
            rec_df = recommend_book_by_book(title, pt, item_similarity, books)
        except: # Traditional filtering using similar title 
            rec_df = rec_by_title(title, books, book_ratings)
            
    # Convert recommendation df into json for API
    return rec_df[['isbn','title','author','year','pub','Image-URL-L']].to_dict(orient="records")



