from flask import Flask, render_template

app = Flask(__name__)


@app.route("/Classified")
def home():
    return render_template("index.html")

@app.route("/flag")
def about():
    return render_template("flag.html")

if __name__ == "__main__":
    app.run(debug=True)

