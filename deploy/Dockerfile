FROM alpine:3.3

ARG version=0.21.0
ARG workdir=/opt
RUN rm -rf $workdir
RUN mkdir -p $workdir
COPY kpm-$version.tar.gz $workdir

WORKDIR $workdir
RUN tar xzvf kpm-$version.tar.gz
WORKDIR $workdir/kpm-$version

RUN apk --update add python py-pip openssl ca-certificates git
RUN apk --update add --virtual build-dependencies python-dev build-base wget openssl-dev libffi-dev
RUN pip install pip -U
RUN pip install gunicorn -U \
  && pip install -r requirements.txt -U \
  && python setup.py install


ENTRYPOINT ["gunicorn", "kpm.api.wsgi:app"]
CMD ["-b", ":5000", "--threads", "3", "-w", "1"]
EXPOSE 5000
