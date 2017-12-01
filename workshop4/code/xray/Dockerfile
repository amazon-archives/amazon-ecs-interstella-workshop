FROM amazonlinux
COPY xray /usr/bin/xray
ENTRYPOINT ["/usr/bin/xray", "--bind=0.0.0.0:2000", "log-file /var/log/xray-daemon.log"]