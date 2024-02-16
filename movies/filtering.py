from flask import Blueprint, render_template, request
from surprise import SVDpp, Dataset, Reader
import pandas as pd
import os

bp = Blueprint("filtering", __name__)

# Load your movie data
cwd = os.getcwd()
path = os.path.join(cwd,'movies')
movies_df = pd.read_csv(os.path.join(path,'movies.csv'))
movies_df['title_year'] = movies_df['title'] + ' (' + movies_df['year'].astype(str) + ')'
# Load your rating data
rating_df = pd.read_csv(os.path.join(path,'ratings_cleaned.csv'))

# Load your ratings data and create a Surprise dataset
reader = Reader(line_format='user item rating', rating_scale=(0.5, 10))
data = Dataset.load_from_df(df=rating_df[['userId', 'movieId', 'rating']], reader=reader)
trainset = data.build_full_trainset()

# Create and train the SVDpp algorithm
best_parameters = {'n_factors': 30, 'n_epochs': 40, 'lr_all': 0.03, 'reg_all': 0.02, 'random_state': 0}
model = SVDpp(**best_parameters)
model.fit(trainset)

@bp.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        user = int(request.form['user_id'])
        if user:
            rated_movies, recommended_movies = get_recommendations(model, user=user)
            return render_template("filtering/recommendations.html", user=user,
                            rated_movies=rated_movies, 
                            recommended_movies=recommended_movies)
        else:
            return 'Not Found'
    return render_template("filtering/search.html")


def get_recommendations(model, user=463):
    USER_ID = user
    inner_uid = model.trainset.to_inner_uid(USER_ID) 

    # Get movie recommendations for the given user
    movies_rated_inner = [int(item[0]) for item in model.trainset.ur[inner_uid]] 
    movies_rated_ids = [int(model.trainset.to_raw_iid(item)) for item in movies_rated_inner]
    rated_movies = get_movie_rated(movies_rated_ids)

    unrated_movies_inner = [id for id in model.trainset.all_items() if id not in movies_rated_inner]
    predictions = [model.predict(uid=USER_ID, iid=model.trainset.to_raw_iid(item)) for item in unrated_movies_inner]

    # Sort predictions by estimated rating in descending order
    sorted_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)

    movie_details = get_movie_details(sorted_predictions[:13])

    return rated_movies, movie_details # Return top 9 recommendations

def get_movie_rated(movies_rated_ids):
    movies_list = []
    for id in movies_rated_ids:
        title = movies_df[movies_df["movieId"]==id].title.iloc[0]
        path = movies_df[movies_df['movieId']==id].poster_path.iloc[0]
        poster_path = "https://image.tmdb.org/t/p/w185"+path

        movies_list.append({
            "title": title,
            "poster_path": poster_path
        })
    return movies_list


def get_movie_details(recommendations):
    movies_list = []
    for elem in recommendations:
        movie_id = elem.iid
        rating = round(number=elem.est, ndigits=2) 
        title = movies_df[movies_df["movieId"]==movie_id].title.iloc[0]
        path = movies_df[movies_df['movieId']==movie_id].poster_path.iloc[0]
        poster_path = "https://image.tmdb.org/t/p/w185"+path

        movies_list.append({
            "title": title,
            "rating": rating,
            "poster_path": poster_path,
        })
    return movies_list
