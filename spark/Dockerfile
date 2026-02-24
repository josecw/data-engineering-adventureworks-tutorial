FROM bitnami/spark:3.5

# Install Iceberg dependencies
RUN pip install --no-cache-dir \
    apache-iceberg==1.4.0 \
    pyiceberg==0.6.0 \
    pyspark==3.5.0

# Copy Spark configuration
COPY conf/spark-defaults.conf /opt/bitnami/spark/conf/

# Set working directory
WORKDIR /opt/jobs

# Copy jobs
COPY jobs/ /opt/jobs/

# Make scripts executable
RUN chmod +x /opt/jobs/*.py

# Default command
CMD ["/opt/bitnami/spark/bin/spark-submit", "--help"]
