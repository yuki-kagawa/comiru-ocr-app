FROM python:3.11-slim

# 必要パッケージのインストール
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean

# 高精度モデル(jpn.traineddata from tessdata_best)をダウンロード
RUN mkdir -p /usr/share/tesseract-ocr/4.00/tessdata && \
    curl -L -o /usr/share/tesseract-ocr/4.00/tessdata/jpn.traineddata \
    https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata

# 作業ディレクトリ作成
WORKDIR /app

# 依存ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションのコピー
COPY . .

# 静的ファイル収集
RUN python manage.py collectstatic --noinput
# RUN python manage.py migrate

# アプリケーション起動
CMD ["gunicorn", "sqlServerProject.wsgi:application", "--bind", "0.0.0.0:10000"]
