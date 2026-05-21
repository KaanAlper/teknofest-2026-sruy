# CargoBot Python çekirdeği (mock + dev) için minimal image.
# Robot Jetson tarafında bu image değil, native ROS2 Humble + sistem Python
# kullanılır. Bu Dockerfile sadece lokal sim'in CargoBot konteynerine yarar.

FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .[dev]

COPY src ./src
COPY tests ./tests

ENV PYTHONPATH=/workspace/src

CMD ["python", "src/main.py", "--headless"]
