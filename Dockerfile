FROM python:3.11-slim-bullseye
ENV FLASK_APP=src \
    SQLALCHEMY_DB_URI=postgresql+psycopg2://default:endpoint=ep-solitary-paper-a16sp7x5;W7RcAkO9ZbmY@ep-solitary-paper-a16sp7x5.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require \
    JWT_SECRET_KEY='JWT_SECRET_KEY' \
    CLOUDINARY_URL=cloudinary://357134227668635:n9zKXiUhV6qM9KiUdK6nzUVeOrw@dujstsjog

WORKDIR /src
COPY requirements.txt .
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 libpq-dev gcc  -y
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install scipy
RUN pip3 install -r requirements.txt
RUN pip install wheel setuptools pip --upgrade
RUN pip3 install --timeout 10000 -U opencv-python-headless
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip3 install -U flask_cors
COPY . .
CMD ["flask", "run"]