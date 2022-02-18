from flaskblog import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context(): #to push application context.
        db.create_all()
    app.run(debug=True)