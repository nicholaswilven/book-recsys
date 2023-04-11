import numpy as np

from traditional_filtering import *
from collaborative_filtering import *
from load_data import *

from fastapi import FastAPI, HTTPException
app = FastAPI()

def wrap_data(df,message = None):
    """Function to wrap recommendation result into Standard JSON API response format
    Args: 
      df: top 10 recommendation dataframe
      message: Information about recommendation used 
    Output:
      response: Standard JSON API response format"""
    response = {}
    response['message'] = message
    response['data'] = df[['isbn','title','author','year','pub','Image-URL-L']].to_dict(orient="records")
    return response

# Get recommendation for user, will use cf model when possible. Set no_cf=True to always get traditional filtering result
@app.get("/api/v1/rec/user")
async def get_user_rec(user_id:int, no_cf = False):
    if not user_id in list(users['user_id']):
        raise HTTPException(status_code=404, detail="No existing user with this id. Please register first")
    try: # Collaborative filtering will fail if user have no ratings for famous books
        if no_cf:
            raise Exception('Request asked for no collaborative filtering')
        rec_df = recommend_book_to_user(user_id, pt, item_similarity, books, book_ratings)
        rec_model = "collaborative_filtering_user"
    except: # Traditional filtering using age if available or universal rating
        age = users[users['user_id']==user_id]['age'].iloc[0]
        if np.isnan(age):
            rec_df = rec_by_pop(u_ratings, books)
            rec_model = "traditional_filtering_user_age"
        else:
            rec_df = rec_by_age(age, users, books, book_ratings)
            rec_model = "traditional_filtering_user"
    # Convert recommendation df into json for API
    return wrap_data(rec_df, rec_model)

# Get recommendation for book, will use cf model when possible. Set no_cf=True to always get traditional filtering result
@app.get("/api/v1/rec/book")
async def get_book_rec(title, no_cf = False):
    try: # Collaborative filtering will fail if book is not a famous books
        if no_cf:
            raise Exception('Request asked for no collaborative filtering')
        rec_df = recommend_book_by_book(title, pt, item_similarity, books)
        rec_model = "collaborative_filtering_book"
    except: # Traditional filtering using similar title 
        rec_df = rec_by_title(title, books, book_ratings) 
        rec_model = "traditional_filtering_book"   
    # Convert recommendation df into json for API
    return wrap_data(rec_df, rec_model)


'''
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

db: List[User] = [
    User(user_id=
         )
]

json_users = [User(**u) for u in json.load(open("file.json"))]


@app.post("/api/v1/users")
async def register_user(user : User):
    db.append(user)
    return {"user_id":user.user_id}

'''
