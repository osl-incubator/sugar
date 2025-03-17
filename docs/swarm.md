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
backend: compose
env-file: .env
defaults:
  profile: profile1
  project-name: sugar
profiles:
  profile1:
    project-name: project1
    config-path: tests/containers/profile1/compose.yaml
    env-file: .env
    services:
      default: service1-1,service1-3
      available:
        - name: service1-1
        - name: service1-2
        - name: service1-3
  profile2:
    config-path: tests/containers/profile2/compose.yaml
    env-file: .env
    services:
      available:
        - name: service2-1
        - name: service2-2
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

Deploy a stack from a sugar compose file:

```bash
$ sugar swarm deploy --stack my_stack --file ./.sugar-prod.yml
```

or

if `.sugar.yml` file is present in the your current project root directory

```bash
$ sugar swarm deploy --stack my_stack
```

You can also use a `profile2` compose file:

```bash
$ sugar swarm deploy --stack my_stack --profile profile2
```

### List Services in a Stack

List services in a specific stack:

```bash
$ sugar swarm ls --stack my_stack
```

### List Tasks in a Stack

List the tasks in a stack:

```bash
$ sugar swarm ps --stack my_stack
```

### Remove a Stack

Remove a deployed stack:

```bash
$ sugar swarm rm --stack my_stack
```

## Service Management

### List All Services

List all services in the swarm:

```bash
$ sugar swarm ls
```

List all services in a specific stack in the swarm

```bash
$ sugar swarm ls --stack my_stack
```

### Inspect Services

Get detailed information about a service:

```bash
$ sugar  swarm inspect --service service1-1 --stack my_stack
```

### View Service Logs

View logs for a specific service:

```bash
$ sugar swarm logs --services service1-1 --stack my_stack
```

With additional options:

```bash
$ sugar swarm logs --services myservice --stack my_stack --follow --tail 100
```

### Scale Services

Scale services within a stack:

```bash
$ sugar swarm scale --stack my_stack --replicas service1=3,service2=5
```

### Update Services (Currently in experemental stage)

Update service configuration:

```bash
$ sugar swarm update --services myservice --image nginx:latest
```

Update with environment variables:

```bash
$ sugar swarm update --services myservice --env_add "DEBUG=1,LOG_LEVEL=info"
```

### Rollback Services

Rollback a set of services to its previous configuration:

```bash
$  sugar swarm rollback --services service1-1,service1-3 --stack my_stack
```

Rollback all services in a stack:

```bash
$ sugar swarm rollback --stack my_stack --all
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

Production Profile:

```bash
$ sugar --profile production swarm deploy --stack my_stack
```

Development Profile:

```bash
$ sugar --profile dev swarm deploy --stack my_stack
```

Testing Profile:

```bash
$ sugar --profile test swarm deploy --stack my_stack
```

This allows you to maintain different configurations for different environments
within the same project.
