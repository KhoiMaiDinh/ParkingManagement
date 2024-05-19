FROM python:3.11-slim-bullseye
ENV FLASK_APP=src \
    SQLALCHEMY_DB_URI=sqlite:///car_parking.db \
    JWT_SECRET_KEY='JWT_SECRET_KEY' \
    CLOUDINARY_URL=cloudinary://357134227668635:n9zKXiUhV6qM9KiUdK6nzUVeOrw@dujstsjog

WORKDIR /src
COPY requirements.txt .
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install scipy
RUN pip3 install -r requirements.txt
RUN pip install wheel setuptools pip --upgrade
RUN pip3 install --timeout 10000 -U opencv-python-headless
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
COPY . .
CMD ["flask", "run"]