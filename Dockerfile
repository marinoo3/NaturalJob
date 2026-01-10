# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.11

# RUN useradd -m -u 1000 user
# USER user
# ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python -m spacy download fr_core_news_sm
RUN python -m nltk.downloader stopwords

COPY . /app

EXPOSE 7860

CMD ["gunicorn", "--bind", ":7860", "--timeout", "1200", "--threads", "6", "app:app"]

