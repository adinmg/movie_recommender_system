from flask import Blueprint, render_template

bp = Blueprint("hybrid", __name__)

@bp.route("/search", methods=["GET"])
def search():
    
    return render_template("hybrid/search.html")