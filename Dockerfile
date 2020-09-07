FROM rstudio/r-base:3.6-xenial
LABEL maintainer="Harsh Bandhey <raptor419heavy@gmail.com>"

# install python

RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

# Set default locale
ENV LANG C.UTF-8

# Set default timezone
ENV TZ UTC

COPY ./hilbert/install_packages.R install_packages.R

RUN Rscript install_packages.R

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt 

EXPOSE 5000

ENTRYPOINT [ "python" ] 

CMD [ "app.py" ] 