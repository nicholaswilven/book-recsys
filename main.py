import pandas as pd
import numpy as np

from traditional_filtering import *
from collaborative_filtering import *
from load_data import *

def generate_recommendation(user_id = None, title = None, no_cf = False):
    if user_id != None:   # When given user_id, will use user_id for giving recommendation
        if user_id not in users['user_id']:
            raise HTTPException(status_code=404, detail="No existing user with this id. Please register first")
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

# Load data
books = load_books()
ratings = load_ratings()
users = load_users()

book_ratings = pd.merge(ratings, books, on='isbn')
u_ratings = get_u_ratings(book_ratings)
pt, item_similarity = user_based_cf(book_ratings)

from fastapi import FastAPI, HTTPException
app = FastAPI()

# Get recommendation for user, will use cf model when possible.
@app.get("/api/v1/rec/user")
async def user_rec(user_id):
    return generate_recommendation(user_id = user_id)

# Get recommendation for book, will use cf model when possible.
@app.get("/api/v1/rec/book")
async def book_rec(title):
    return generate_recommendation(title = title)

# Get recommendation for user with traditional filtering.
@app.get("/api/v1/rec_tf/user")
async def user_rec_tf(user_id):
    return generate_recommendation(user_id = user_id, no_cf= True)

# Get recommendation for book with traditional filtering.
@app.get("/api/v1/rec_tf/book")
async def book_rec_tf(title):
    return generate_recommendation(title = title, no_cf= True)

# [Fail] Register new user via API
@app.post("/api/v1/user/register")
async def user_register(age, location):
    # user_id = users[users['user_id']].max+1
    new_user = {'user_id': 42,
                'age':age,
                'location':location}
    # users = users.concat(new_user, ignore_index=True)
    return new_user

# [Fail] Post new rating for user
@app.post("/api/v1/user/rating")
async def submit_rating(user_id, rating, isbn, title):
    if title != None:
        try:
            isbn = '0971880107' #books[books['title']==title]['isbn'].iloc[0]
        except:
            raise HTTPException(status_code=404, detail='No book with such title!')
    if isbn != None:
        new_rating = {'user_id':user_id,
                      'rating':rating,
                      'isbn':isbn}
        # ratings = ratings.concat(new_rating, ignore_index=True)
    return new_rating

