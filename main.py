from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def welcome_page():
    return render_template("welcome_page.html")


@app.route("/registration")
def registration():
    return render_template("registration.html")


if __name__ == "__main__":
    app.run(debug=True)
