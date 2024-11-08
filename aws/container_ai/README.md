# Project: Access AWS Services From Docker

WORK IN PROGRESS


## Docker 

```bash
docker build -t ecs1/server .
docker container run -d -p 9090:9090 ecs1/server
docker ps
docker stop <container id>
docker tag ecs1/server 598185244415.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
```

### ECR

```bash
aws config
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 598185244415.dkr.ecr.us-east-1.amazonaws.com
docker push 598185244415.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
```

### ECS



#### Create Cluster

#### Create Task
under Task roles 
add roll that has access to s3 and rekognition Task role
598185244415.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
Port mappings Container port to external port

#### Run Task In Cluster

On Task Definitions screen, select defined task, select Deploy->run, then deploy to cluster created previously, create task button

A Public IP will be available on the cluster tasks configuration screen, try opening that in your browser. Be sure to use the correct port.

if you are denied access, confirm the port mappings for the task the security group in the Networking tab. If you find problems, stop the task in the cluster, edit the task. a new version should be availble. run the task.
