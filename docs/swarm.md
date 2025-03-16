# Sugar Swarm Commands

Sugar provides support for Docker Swarm commands through its swarm extension.
This allows you to manage Docker Swarm clusters, services, and stacks using a
simplified interface.

## Overview

The swarm extension provides commands for:

- Initializing and joining swarm clusters
- Deploying, inspecting, and removing stacks
- Managing swarm services (listing, scaling, updating, rolling back)
- Managing swarm nodes

## Configuration

To use the swarm extension, you need to set the backend to `swarm` in your
`.sugar.yaml` configuration file:

```yaml
backend: swarm
env-file: .env
defaults:
  profile: "profile-defaults"
profiles:
  profile-defaults:
    config-path: docker-compose.yml
    services:
      available:
        - name: service1
        - name: service2
```

## Basic Commands

### Initialize a Swarm

Initialize a new Docker Swarm on the current engine:

```bash
$ sugar swarm init --options "--advertise-addr 192.168.1.1"
```

### Join a Swarm

Join an existing swarm as a worker or manager node:

```bash
$ sugar swarm join --options "--token SWMTKN-1-... 192.168.1.1:2377"
```

## Stack Management

### Deploy a Stack

Deploy a stack from a compose file:

```bash
$ sugar swarm deploy --stack myapp --file ./docker-compose.yml
```

You can also use a profile-defined compose file:

```bash
$ sugar swarm deploy --stack myapp --profile profile-defaults
```

### List Services in a Stack

List services in a specific stack:

```bash
$ sugar swarm ls --stack myapp
```

### List Tasks in a Stack

List the tasks in a stack:

```bash
$ sugar swarm ps --stack myapp
```

### Remove a Stack

Remove a deployed stack:

```bash
$ sugar swarm rm --stack myapp
```

## Service Management

### List All Services

List all services in the swarm:

```bash
$ sugar swarm ls
```

### Inspect Services

Get detailed information about a service:

```bash
$ sugar swarm inspect --services myservice
```

### View Service Logs

View logs for a specific service:

```bash
$ sugar swarm logs --services myservice
```

With additional options:

```bash
$ sugar swarm logs --services myservice --follow --tail 100
```

### Scale Services

Scale services within a stack:

```bash
$ sugar swarm scale --stack myapp --replicas service1=3,service2=5
```

### Update Services

Update service configuration:

```bash
$ sugar swarm update --services myservice --image nginx:latest
```

Update with environment variables:

```bash
$ sugar swarm update --services myservice --env_add "DEBUG=1,LOG_LEVEL=info"
```

### Rollback Services

Rollback a service to its previous configuration:

```bash
$ sugar swarm rollback --services myservice
```

Rollback all services in a stack:

```bash
$ sugar swarm rollback --stack myapp --all
```

## Node Management

Sugar provides a complete set of commands to manage swarm nodes through the
`node` subcommand:

### List Nodes

```bash
$ sugar swarm node ls
```

### Inspect Nodes

```bash
$ sugar swarm node --inspect node-id1,node-id2
```

### Promote Nodes

Promote a worker node to manager:

```bash
$ sugar swarm node --promote node-id
```

### Demote Nodes

Demote a manager node to worker:

```bash
$ sugar swarm node --demote node-id
```

### List Tasks on a Node

```bash
$ sugar swarm node --ps node-id
```

### Remove Nodes

```bash
$ sugar swarm node --rm node-id
```

### Update Nodes

```bash
$ sugar swarm node --update node-id --options "--availability drain"
```

## Command Options

Most swarm commands accept the following common options:

- `--profile`: Specify the profile name to use
- `--options`: Pass additional options to the underlying Docker command
- `--services`: Specify a comma-separated list of services
- `--all`: Apply the command to all services
- `--stack`: Specify a stack name for stack operations

## Advanced Usage

### Using Multiple Options

You can combine multiple options for complex operations:

```bash
$ sugar swarm update --services web-service --image nginx:alpine --replicas 3 --detach --env_add "MODE=production,DEBUG=false"
```

### Using with Profiles

Leverage Sugar profiles to manage different Swarm configurations:

```bash
$ sugar --profile production swarm deploy --stack myapp
```

This allows you to maintain different configurations for different environments
within the same project.
