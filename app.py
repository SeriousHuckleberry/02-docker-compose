from flask import Flask
import psycopg

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>🚀 DevOps Portfolio Project</h1>
    <p>Hello from Flask!</p>
    <p>Running with Docker Compose!</p>
    """


@app.route("/db")
def database():
    try:
        connection = psycopg.connect(
            host="postgres",
            port=5432,
            dbname="flaskdb",
            user="postgres",
            password="postgres"
        )

        connection.close()

        return "PostgreSQL connection successful!"

    except Exception as e:
        return f"Database connection failed: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)