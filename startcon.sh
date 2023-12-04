#!/bin/bash

# Add your commands to .bashrc
echo 'python3 /rosiecon/RosieCon2023Sem2/start.py' >> ~/.bashrc

# Add a delay
echo "Waiting before attempting SSH connection..."
sleep 30  # waits for 30 seconds

# Start the SSH connection in the background
nohup ssh -tt -i /root/.ssh/rosiekey.pem -o UserKnownHostsFile=/root/.ssh/rosiekeyhost ubuntu@ec2-52-62-118-55.ap-southeast-2.compute.amazonaws.com > /rosiecon/RosieCon2023Sem2/rosie.out & disown

# Wait for the SSH connection to be established
while ! ssh -q -o BatchMode=yes -o ConnectTimeout=5 ubuntu@ec2-52-62-118-55.ap-southeast-2.compute.amazonaws.com exit; do
    echo "Waiting for SSH connection..."
    sleep 20
done

# Continue with the rest of the script
echo "SSH connection established, continuing with script..."
