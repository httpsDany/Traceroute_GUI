FROM jenkins/jenkins:lts

USER root

# Install Docker CLI inside Jenkins
RUN apt-get update && \
    apt-get install -y docker.io && \
    rm -rf /var/lib/apt/lists/*

# Add jenkins user to docker group (ignore if group exists)
RUN groupadd -f docker && \
    usermod -aG docker jenkins

USER jenkins

