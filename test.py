from load_data import *
from main import generate_recommendation
#books = load_books()
#ratings = load_ratings()
users = load_users()

if __name__=="__main__":
    print(generate_recommendation(user_id = 276688))