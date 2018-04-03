#!/bin/bash
mkdir /home/ec2-user/.docker
cat << EOF > /home/ec2-user/.docker/config.json
{
	"credsStore": "ecr-login"
}
EOF
chown -R ec2-user. /home/ec2-user/.docker
git clone https://github.com/awslabs/amazon-ecr-credential-helper.git
cd amazon-ecr-credential-helper && make docker && cp bin/local/docker-credential-ecr-login /usr/local/bin/
