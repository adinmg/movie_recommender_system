from flask import Flask, render_template, request
import pandas as pd
from surprise import SVDpp
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split, cross_validate
from surprise import accuracy

app = Flask(__name__)

# Load your ratings data and create a Surprise dataset
# Replace 'path/to/ratings.csv' with the path to your ratings file
reader = Reader(line_format='item user rating', sep=',', skip_lines=1, rating_scale=(0.5, 10))
ratings_data = Dataset.load_from_file('../ratings_cleaned.csv', reader=reader)
trainset, _ = train_test_split(ratings_data, test_size=0.25, shuffle=True)

# Create and train the SVDpp algorithm
optimal_svd = SVDpp(n_factors=15, n_epochs=25, lr_all=0.012, reg_all=0.02)
optimal_svd.fit(trainset)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        recommendations = get_recommendations(user_id)
        return render_template('index.html', user_id=user_id, recommendations=recommendations)
    return render_template('index.html')

def get_recommendations(user_id):
    # Get movie recommendations for the given user
    all_movie_ids = set(elem[1] for elem in ratings_data.raw_ratings)
    movies_rated_user = {elem[1] for elem in ratings_data.raw_ratings if elem[0] == user_id}
    user_not_rated_movies = all_movie_ids - movies_rated_user
    testset = [(user_id, movie_id, 0) for movie_id in user_not_rated_movies]
    predictions = optimal_svd.test(testset)
    recommendations = [(int(prediction.iid), round(prediction.est,2)) for prediction in predictions]
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:10]  # Return top 10 recommendations

if __name__ == '__main__':
    app.run(debug=True)
