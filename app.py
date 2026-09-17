from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    search_term = None

    if request.method == "POST":
        search_term = request.form.get("search_term")

    return render_template(
        "index.html",
        search_term=search_term
    )


if __name__ == "__main__":
    app.run(debug=True)