
# Imports

import pandas as pd
import numpy as np
import re
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Global objects

ratings=pd.read_csv('ratings.csv')
ratings.drop('timestamp', inplace=True, axis=1)
movies=pd.read_csv('movies.csv')
movies.drop('genres',inplace=True,axis=1)
ratings=pd.merge(movies,ratings)
movieRatings=ratings.pivot_table(index=['userId'],columns=['title'],values='rating')
corrMatrix=movieRatings.corr(method='pearson', min_periods=100)



#Function to return top 10 movies based on a given user's watch history using item based collaborative filtering:

def CollaborativeBasedFiltering(user_id):

    myRatings=movieRatings.loc[user_id].dropna()
    simCandidates=pd.Series(dtype="float64")
    same=[]
    for i in range(len(myRatings.index)):
        sims=corrMatrix[myRatings.index[i]].dropna()
        sims=sims.map(lambda x:x*myRatings[i])
        simCandidates=simCandidates.append(sims)
    simCandidates.sort_values(inplace=True, ascending=False)
    simCandidates=simCandidates.groupby(simCandidates.index).sum()
    simCandidates.sort_values(inplace=True, ascending=False)
    
    same=[]
    for movie in myRatings.index:
        if(movie in simCandidates.index):
            same.append(movie)
            
    ddf=pd.DataFrame(simCandidates)
    filteredCandidates=ddf
    for movie in same:
        filteredCandidates=filteredCandidates.drop(movie)
    filteredCandidates.columns=['Rating']

    return filteredCandidates



def UserMovies(user_id):
    myRatings=movieRatings.loc[user_id].dropna()
    print('Top Movies rated by user are :')
    print(myRatings.sort_values(ascending=False).head(10))
    print()
    print('Lowest rated movies by user are :')
    print(myRatings.sort_values(ascending=True).head(10))
    print()
    


def ContentBasedFiltering(movie):
    df = pd.read_csv("Content_movie_dataset.csv")
    features = ['keywords','cast','genres','director']
    
    def combine_features(row):
        return row['keywords']+" "+row['cast']+" "+row['genres']+" "+row['director']
    
    def get_title_from_index(index):
        return df[df.index == index]["title"].values[0]
    
    def get_index_from_title(title):
        return df[df.title == title]["index"].values[0]
    
    for feature in features:
        df[feature] = df[feature].fillna('') #filling all NaNs with blank string

    df["combined_features"] = df.apply(combine_features,axis=1)
    
    for feature in features:
        df[feature] = df[feature].fillna('')
        
    cv = CountVectorizer() #creating new CountVectorizer() object
    count_matrix = cv.fit_transform(df["combined_features"])
    cosine_sim = cosine_similarity(count_matrix)
    
    movie_user_likes=movie
    movie_index = get_index_from_title(movie_user_likes)
    #accessing the row corresponding to given movie to find all the similarity scores 
    #for that movie and then enumerating over it
    similar_movies = list(enumerate(cosine_sim[movie_index])) 
    sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)[1:]
    print("Top similar movie to "+movie_user_likes+" is:")
    print(get_title_from_index(sorted_similar_movies[0][0]),"\n")
    return get_title_from_index(sorted_similar_movies[0][0])


def HybridRecommender(userid):
    
    filteredCandidates=CollaborativeBasedFiltering(userid)
    
    FinalRecommendations = []
    for movie in filteredCandidates.index[0:10]:

        # removing text in brackets
        movie=re.sub(r"\([^()]*\)", "", movie)
        # pre processing movie title : "Shawshank Redemption, The" -> "The Shawshank Redemption"
        if(", " in movie):
            movie=movie.split(", ")[1] +""+movie.split(", ")[0]
        try:

            recom = ContentBasedFiltering(movie)
            FinalRecommendations.append(recom)

        except:
            print(f"No other similar movies found for :{movie}")
            print()
            FinalRecommendations.append(movie)
            
    Hybrid_Recomm = set(FinalRecommendations).union(set(filteredCandidates.index[0:10])) 

    
    UserMovies(userid)
    print("------------------------------------------Recommended Movies---------------------------------------------")
    print(Hybrid_Recomm)

    

userID =int(input("Enter a User ID : "))

HybridRecommender(userID)






