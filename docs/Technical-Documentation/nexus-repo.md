# Nexus Artifact Repository

We are using Nexus as an artifact store in order to retain docker images and other artifacts needed for our apps and pipelines.

Nexus UI can be accessed at [https://tdp-nexus.dev.raftlabs.tech/](https://tdp-nexus.dev.raftlabs.tech/)

## Nexus Image Management

### Host Information

The VM that runs the [Sonatype Nexus Image](https://help.sonatype.com/repomanager3/product-information/download) currently resides at 172.10.4.102 on Raft's internal network. You must first be connected to the labs.goraft.tech Raft Labs VPN before SSHing to the container. Current points of contact for getting setup with the VPN are Connor Meehan and Barak Stout.

### Nexus Container Setup

From our virtual machine, here is how to get Nexus up and running.
Pull and run nexus image:
```
docker pull sonatype/nexus3
docker volume create --name nexus-data
docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 --name nexus -v nexus-data:/nexus-data sonatype/nexus3
```

wait for nexus to be running
```
docker logs -f nexus
```

The first time you need to log in as root, you will need the auto-generated admin password that is created upon initialization of the container.
exec into the container and get docker admin.password:
```
docker exec -it nexus /bin/bash
cat /nexus-data/admin.password
```

After logging in as root for the first time, you will be taken to a page to set a new password.

## Hosted Docker Repository

### Setup

In order to use Nexus as a Docker repository, the DNS for the repo needs to be able to terminate https. We are currently using cloudflare to do this.

When creating the repository (must be signed in with admin privileges), since the nexus server isn't actually terminating the https, select the HTTP repository connector. The port can be anything you assign, as long as the tool used to terminate the https connection forwards the traffic to that port. 

In order to allow [Docker client login and connections](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/docker-registry/docker-authentication) you must set up the Docker Bearer Token Realm in Settings -> Security -> Realms -> and move the Docker Bearer Token Realm over to Active.
Also, any users will need nx-repository-view-docker-#{RepoName}-(browse && read) at a minimum and (add and edit) in order to push images.

We have a separate endpoint to connect specifically to the docker repository.
[https://tdp-docker.dev.raftlabs.tech](tdp-docker.dev.raftlabs.tech)

e.g. `docker login https://tdp-docker.dev.raftlabs.tech`

### Pushing Images

Before an image can be pushed to the nexus repository, it must be tagged for that repo:

`docker image tag ${ImageId} tdp-docker.dev.raftlabs.tech/${ImageName}:${Version}`

then you can push:

`docker push tdp-docker.dev.raftlabs.tech/${ImageName}:${Version}`

### Pulling Images

We have set up a proxy mirror to dockerhub that can pull and cache DockerHub images.
Then we have created a group docker repository that can be pulled from. If the container is in our hosted repo, the group will return that container. If not, it will see if we have a cached version of that container in our proxy repo and, if not, pull that from dockerhub, cache it and allow the docker pull to happen.

`docker pull https://tdp-docker-store.dev.raftlabs.tech/${ImageName}:${Version}`