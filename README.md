# containers-sugar

Simplify the usage of containers.

You may be thinking, why do I need a new library that wrap-up
docker-compose or podman-compose if they are already really simple to use?

Yes, they are simple to use, but if you have some other parameters to
the compose command line, it could be very tedious to write them every time
such as `--env-file`, `--project-name`, `--file`, etc.

So, in this case we could use something like a script or `make`, right?

Yes, and just for one project it would be good enough. But, if you maintain
or collaborate a bunch of projects, it would be like a boiler plate.

Additionally, if you are maintaining some extra scripts in order to improve
your containers stack, these scripts would be like a boilerplate as well.

So, the idea of this project is to organize your stack of containers,
gathering some useful scripts and keeping this information centralized in a
configuration file. So the command line would be very simple.


* Free software: BSD 3 Clause
* Documentation: https://osl-incubator.github.io/containers-sugar


## Features

The commands from docker-compose available are:

* build
* config
* create
* down
* events
* exec
* images
* kill
* logs
* pause
* port
* ps
* pull
* push
* restart
* rm
* run
* start
* stop
* top
* unpause
* up
* version

These commands are available in the main profile/plugin, so
you don't need to specify any extra parameter to access them.

For extra commands, we are gathering them into a profile/plugin called
`ext`, so you can access them using something like: `sugar ext restart`.

The current available **ext** commands are:

* start -> alias for `up`
* restart -> runs `stop` and `up`


## How to use it

First you need to place the config file `.containers-sugar.yaml` in the root
of your project. This is an example of a configuration file:

```yaml
version: 1.0
compose-app: docker-compose
default:
  group: {{ env.ENV }}
service-groups:
  - name: group1
    project-name: project1
    compose-path: containers/tests/group1/compose.yaml
    env-file: .env
    services:
      default:
        - service1
        - service3
      available:
        - name: service1
        - name: service2
        - name: service3
  - name: group2
    project-name: null
    compose-path: containers/tests/group2/compose.yaml
    env-file: .env
    services:
      # default: null
      available:
        - name: service1
        - name: service1
```

**NOTE**: containers-sugar has an convenient alias `sugar` that helps to
keep the command line shorter, where **k** stands for *containers*,
**x** stands for *su* (*shu* sound), and **gr** stands for *gar*.
In another words, you can use `containers-sugar` or `sugar` CLI.

Some examples of how to use it:

* build the defaults services (service1,service3) for group1:
  `sugar build --group group1`

* build the all services (there is no default service defined) for group2:
  `sugar build --group group2`

* build all services (ignore default) for group1:
  `sugar build --group group1 --all`

* start the default services for group1:
  `sugar ext start --group group1`

* restart all services (ignore defaults) for group1:
  `sugar ext restart --group group1 --all`

* restart service1 and service2 for group1:
  `sugar ext restart --group group1 --services service1,service2`


**NOTE**: If you use: ```default: group: {{ env.ENV }}```, you don't need to
give `--group <GROUP_NAME>`, except if you want a different group than the
default one.
