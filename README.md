kmad-web is a web service for alignment, annotation and disorder prediction
of intrinsically disordered proteins.
[www.cmbi.umcn.nl/kmad-web](http://www.cmbi.umcn.nl/kmad-web).

# Installation

The following sections describe how to setup development and production
environments using docker.

## Dependencies

There are only two dependencies because docker is used for development,
testing, and deployment.

* docker >= 1.12.3
* docker-compose >= 1.8.1

Follow the instructions on the docker website to install docker for your
system. docker-compose can be installed system-wide using pip.

## Development

Fork [the repository](https://github.com/cmbi/kmad-web) to your own account
and then clone the fork:

    git clone git@github.com:<youraccount>/kmad-web

Add the upstream repository:

    cd kmad-web
    git remote add upstream git@github.com:cmbi/kmad-web

In the project folder, build the docker images:

    docker-compose build --force-rm

To start the development environment, run:

    ./run_dev.sh

During development the various containers are configured to restart the
contained application if code changes are detected. This removes the need to
restart containers after every change; however, because celery is used and some
tasks can take a long time to finish, restarting in the middle of a job may
cause undesired side-effects.

## Deployment

Currently deployment is manual and follows a similar process as the development
environment.

Log in to the production machine and clone the upstream project:

    git clone git@github.com:cmbi/kmad-web


In the project folder, build the docker images:

    docker-compose build --force-rm

To run the container in production:

    docker-compose up -d
