# Book Recommendation System

Dataset:
- Books: List of books with title, author, publisher, year published, ISBN, url for book cover
- Users: List of users_id with age and location
- Ratings: List of ratings with user_id , ISBN and rating

Model used:
1. User based Collaborative Filtering: Save memory and running time by taking most famous book and ratings from top user. Similarity Matrix are computed using Cosine Similarity dan Pearson Correlation (defaults to cosine). Implemented to give book recommendation for a user (with ratings) or for a single book.
2. Traditional Filtering: Complement to Collaborative Filtering when requirements are not met. Available filters: 
    [a] Most popular books all time (rating count) 
    [b] Most popular books in a age group 
    [c] Similar title book

Notes:
In addition of above mentioned method, I also tried to implement Personalized Page Rank algorithm and Knowledge Graph method. Personalized Page Rank fails since have too many nodes in a graph, making the score for books too low for sorting. Knowlegde Graph based method are not suitable for current data features (need more features to induce connection between books).

API:
- /api/v1/rec/user?user_id=XX : gives top 10 recommendation for user with user_id XX. Model used to generate recommendation defaults to [1], in case failed will use [2b]. then [2a].
- /api/v1/rec/book?title=XX : gives top 10 recommendation for book similar to book with title XX. Model used to generate recommendation defaults to [1], in case failed will use [2c].
- /api/v1/rec_tf/user?user_id=XX : gives top 10 recommendation for user with user_id XX. Model used to generate recommendation defaults [2b] then [2a].
- /api/v1/rec_tf/book?title=XX : gives top 10 recommendation for book similar to book with title XX. Model used to generate recommendation defaults to [2c].
    
Quick Start Guide:
1. Install requirements ```pip install -r requirements.txt```
2. Place "Books.csv", "Users.csv", "Ratings.csv" to folder "data"
3. Run at bash ```uvicorn main:app --reload```
4. Test out the API