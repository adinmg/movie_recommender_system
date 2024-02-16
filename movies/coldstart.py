from flask import Blueprint, request, render_template
from movies.models import Collection
import pandas as pd
import os

bp = Blueprint("coldstart", __name__)

# Load your movie data
cwd = os.getcwd()
path = os.path.join(cwd,'movies')
df = pd.read_csv(os.path.join(path,"movies.csv"))

@bp.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        title = request.form["title"]
        if title:
            movies = get_recommendations(title)
            return render_template("coldstart/recommendations.html", movies=movies)
        else:
            return 'Not Found'
    return render_template("coldstart/search.html")


def get_recommendations(title):
    query_results = Collection.query(
        query_texts=[f"Find me some movies related to {title}"],
        n_results=20,
    )
    
    ids = [int(id) for id in query_results['ids'][0]]

    titles = df[df['movieId'].isin(ids)]['title'].tolist()
    poster_path = df[df['movieId'].isin(ids)]['poster_path'].tolist()
    years = df[df['movieId'].isin(ids)]['year'].tolist()

    movie_list = []
    for title, year, path in zip(titles, years, poster_path):
        movie_list.append({
            "title": f"{title} ({year})",
            "poster_path": "https://image.tmdb.org/t/p/w185"+path
        })
    return movie_list
