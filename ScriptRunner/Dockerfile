FROM alpine:latest

LABEL maintainer="Kennedy Technologies, LLC"

# Install necessary tools
RUN apk update && apk add --no-cache bash curl docker-cli dos2unix

# Set the working directory
WORKDIR /scripts

# Copy the backup script into the container
COPY *.sh .
COPY crontab /etc/crontabs/root

# Make the backup script executable
RUN chmod +x *.sh
RUN find . -type f -name "*.sh" -exec dos2unix {} \;

# Start the backup script
CMD ["crond", "-f"]
