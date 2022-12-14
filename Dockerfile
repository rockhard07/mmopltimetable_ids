# app/Dockerfile

FROM python:3.10

CMD mkdir /streamlit_tt

EXPOSE 8501

WORKDIR /streamlit_tt

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/rockhard07/mmopltimetable_ids.git .

RUN pip3 install -r requirements.txt

RUN pip3 install streamlit --upgrade

#ENTRYPOINT ["streamlit", "run"]

#CMD ["main.py"]

CMD streamlit run main.py --server.port $PORT
#CMD streamlit run main.py
