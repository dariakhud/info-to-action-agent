from src.core.log import configure_logging
from src.app.typer import app

# Configure logging on startup
configure_logging()

if __name__ == "__main__":
    app()
