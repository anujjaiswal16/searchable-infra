#!/bin/bash
set -e

# setup_jenkins_vm.sh
# Purpose: Installs Jenkins, Terraform, Python3, and Git on Amazon Linux 2023
# Usage: sudo ./setup_jenkins_vm.sh

echo ">>> Updating System..."
dnf update -y

echo ">>> Installing Java (Corretto 17)..."
dnf install -y java-17-amazon-corretto-devel

echo ">>> Installing Jenkins..."
wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
dnf install -y jenkins
systemctl enable jenkins
systemctl start jenkins

echo ">>> Installing Git..."
dnf install -y git

echo ">>> Installing Terraform..."
dnf config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
dnf install -y terraform

echo ">>> Installing Python 3 and pip..."
dnf install -y python3 python3-pip

echo ">>> Basic Setup Complete!"
echo "Jenkins is running at http://$(curl -s http://checkip.amazonaws.com):8080"
echo "Initial Admin Password:"
cat /var/lib/jenkins/secrets/initialAdminPassword
