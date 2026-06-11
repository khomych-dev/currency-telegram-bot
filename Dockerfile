FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (only production dependencies)
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .

# Run the bot
CMD ["uv", "run", "python", "-m", "bot.main"]
