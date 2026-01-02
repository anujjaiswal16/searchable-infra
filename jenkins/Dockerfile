FROM jenkins/jenkins:lts

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    zip \
    wget \
    unzip \
    curl \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform (using amd64 for Docker compatibility)
RUN wget https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip \
    && unzip terraform_1.6.6_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && chmod +x /usr/local/bin/terraform \
    && rm terraform_1.6.6_linux_amd64.zip \
    && terraform version

# Install Jenkins Plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

# Add jenkins user to docker group (if docker group exists)
RUN groupadd -f docker && usermod -aG docker jenkins || true

USER jenkins
