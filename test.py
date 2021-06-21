from flask import Flask, render_template, redirect, url_for, flash, request, session


app = Flask(__name__)



@app.route("/")
def home():
    return "<h1>working successfully</h1>"


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)