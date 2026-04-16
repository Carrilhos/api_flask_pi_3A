from app import create_app

app = create_app()
print("RUN.PY EXECUTADO")
if __name__ == "__main__":
    app.run(debug=True)