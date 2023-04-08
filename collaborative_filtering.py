import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from itertools import groupby
from scipy import sparse

def user_based_cf(book_ratings,method='cosine'):
    """ Generate similarity matrix for famous book (for efficiency)
    main purpose: user based collaborative filtering using cosine similarity or Pearson correlation
    Args: 
      book_ratings : merge of books and ratings dataframe
    Output:
      similarity matrix using prefered method
    """
    # Take users with more than 10 reviews as reference
    filtered_users = book_ratings.groupby('user_id').count()['rating']>10
    knowledgable_users = filtered_users[filtered_users].index
    
    # Take only famous books (with 5 reviews)
    filtered_rating = book_ratings[book_ratings['user_id'].isin(knowledgable_users)]
    y = filtered_rating.groupby('title').count()['rating']>=5
    famous_books = y[y].index
    
    # Make pivot table, title as row and user_id as column 
    final_ratings =  filtered_rating[filtered_rating['title'].isin(famous_books)]
    pt = final_ratings.pivot_table(index='title',columns='user_id'
                          ,values='rating')
    pt.fillna(0,inplace=True)
    
    if method=='cosine':
        # Item similarity matrix using cosine similarity
        A_sparse = sparse.csr_matrix(pt)
        item_similarity= cosine_similarity(A_sparse)
    else:
        # Normalize and find Peason correlation of matrix
        matrix_norm = pt.subtract(pt.mean(axis=1), axis = 0)
        item_similarity = matrix_norm.T.corr()
    
    return pt, item_similarity

def recommend_book_by_book(title, pt, item_similarity, books,ban_list=[]):
    """Implementation of user_based_cf
    main purpose: recommend similar book given a book title based on users behaviour
    Args: 
      title : book title (perfect match)
      pt, item_similarity : outputs from user_based_cf
      books : books dataframe
      ban_list : remove title from list of recommendation (already read book)
    Output:
      top 10 books with best similarity score
    """
    # Find row index in pivot table for title, for retrieve similarity score of that book 
    index = np.where(pt.index==title)[0][0]
    similar_books = sorted(list(enumerate(item_similarity[index])),key=lambda x:x[1], reverse=True)[1:]
    # Remove books from ban list
    L_final_title = [pt.index[i[0]] for i in similar_books if not pt.index[i[0]] in ban_list][:10]
    return books[books['title'].isin(L_final_title)].drop_duplicates('title')

def recommend_book_to_user(user_id, pt,item_similarity, books, book_ratings):
    """Implementation of user_based_cf
    main purpose: recommend book based on user behaviour (past reviews)
    Args: 
      user_id : user_id of user receiving recommendation
      pt, item_similarity : outputs from user_based_cf
      book_ratings : merge of books and ratings dataframe
    Output:
      top 10 books with best score (for top 10 past books, take top 10 new books with similarity score * rating past book)
    """
    # Retrieve user data
    userdata = book_ratings[book_ratings['user_id']==user_id]

    # Generate ban list from user reading list
    ban_list = set(userdata['title'])
    
    # Take books available in recommendation list (famous books)
    userdata = userdata[userdata['title'].isin(pt.index)].sort_values('rating', ascending=False)

    if len(userdata) > 0:
        similar_books = []
        # Similar method to recommend_book_by_book, except ave all similarities values before processing score 
        for i in range(0,min(10,len(userdata))):
            index = np.where(pt.index==userdata.iloc[i]['title'])[0][0]
            # Give weights for liked book -> have better similarity score
            similarity_vector = [(j[0],j[1]*userdata.iloc[i]['rating']) for j in list(enumerate(item_similarity[index]))]
            similar_books.extend(similarity_vector)

        # Take maximum score of each books (duplicates if referenced from multiple books)
        similar_books_sorted = []
        for key, group in groupby(similar_books, key=lambda x: x[0]):
            similar_books_sorted.append((key, max([j for i, j in group])))
        
        # Take top 10 best scoring books and not in ban list
        similar_books_sorted = sorted(similar_books_sorted,key=lambda x:x[1], reverse=True)
        L_final_title = [pt.index[i[0]] for i in similar_books_sorted if not pt.index[i[0]] in ban_list][:10]

        return books[books['title'].isin(L_final_title)].drop_duplicates('title')
    else: 
        # In case users have no record of reading (famous books) -> user_based_cf fails
        raise Exception("User have no rating for famous books, cannot use collaborative filtering model")
        return None