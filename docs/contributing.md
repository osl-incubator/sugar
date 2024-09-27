# Contributing

Your contributions are valued and play a significant role in the continuous
improvement of **Sugar**. We welcome contributions of all forms and acknowledge
all efforts.

## How You Can Contribute

Contributions can be made in various ways, outlined below:

### Report Bugs

If you encounter a bug in **Sugar**, please report it via our GitHub issues page
at:
[https://github.com/osl-incubator/sugar/issues](https://github.com/osl-incubator/sugar/issues).

When reporting a bug, kindly include the following information to aid in the
issue's resolution:

- The name and version of your operating system.
- Any relevant details about your setup that might assist in diagnosing the
  issue.
- A step-by-step guide to reproduce the bug.

### Fix Bugs

You can contribute by fixing bugs identified in the GitHub issues. Issues tagged
with both "bug" and "help wanted" are available for anyone to work on.

### Implement Features

Feature development is another way to contribute. Review the GitHub issues for
requested features. Issues labeled with "enhancement" and "help wanted" are open
for implementation.

### Write Documentation

There's always a need for more documentation for **Sugar**. This could be
through enhancing the official documentation, contributing to docstrings, or
sharing knowledge via blog posts, articles, and other media.

### Submit Feedback

Feedback is crucial for project improvement. To submit feedback or propose a
feature:

- File an issue at
  [https://github.com/osl-incubator/sugar/issues](https://github.com/osl-incubator/sugar/issues).
- For feature proposals, please provide a detailed explanation of how the
  feature would function, aim for a narrow scope to facilitate easier
  implementation, and remember, **Sugar** is a volunteer-driven project, and we
  welcome contributions.

## Requirements

Before you begin contributing to the Sugar project, there are several technical
prerequisites and best practices you should be familiar with. This section
outlines the key requirements to ensure a smooth and productive contribution
process.

### Conda Environment

Conda is a versatile tool that provides package, dependency, and environment
management for various programming languages. In the Sugar project, we leverage
Conda to manage virtual environments and package dependencies effectively.

- **Environment Setup**: We strongly advise using a Conda environment while
  working with Sugar. If Conda is not installed on your system, you can download
  it from [Miniforge](https://github.com/conda-forge/miniforge). For an
  introductory overview of Conda, consider watching this
  [Conda Basics video](https://learning.anaconda.cloud/conda-basics).
- **Best Practices**: Avoid installing packages in the base Conda environment.
  Always create and activate a new environment for each project to prevent
  dependency conflicts and ensure a clean workspace.

### Git

Our collaborative efforts are facilitated through Git and GitHub. Understanding
the fundamentals of Git is crucial for effective participation.

- **Learning Resources**: If you're new to Git, we recommend starting with the
  [Software Carpentry Git Lesson](https://swcarpentry.github.io/git-novice/),
  which covers essential Git concepts and workflows.
- **Quick Reference**: For a concise summary of common Git commands, refer to
  this
  [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
  provided by GitHub.
- **Configuration Tips**:
  - To streamline your workflow, configure Git to use `rebase` by default for
    pulling changes with `git config --global pull.rebase true`.
  - Familiarize yourself with the `git rebase` command for updating branches
    from a remote repository. Although more complex, it is preferred over the
    default merge commit strategy. For an in-depth explanation, visit
    [Atlassian's guide on merging vs. rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing).
- **Workflow**: The standard open-source development workflow includes forking a
  repository, cloning the fork locally, and configuring an `upstream` remote for
  the original repository. Detailed instructions can be found in
  [GitHub's guide to configuring a remote for a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/configuring-a-remote-repository-for-a-fork).

### Python

Familiarity with Python and adherence to best practices is important for
contributing to Sugar.

- **Style Guide**: Follow the PEP 8 style guide for Python code, available at
  [PEP8](https://peps.python.org/pep-0008/).
- **Best Practices**: pyOpenSci offers a comprehensive guide for writing Python
  packages, which can be found
  [here](https://www.pyopensci.org/python-package-guide/index.html).
- **Advanced Learning**: To deepen your understanding of Python and general
  programming concepts, consider enrolling in the
  [Design of Computer Programs](https://www.udacity.com/course/design-of-computer-programs--cs212)
  course on Udacity. Though challenging and based on Python 2, it provides
  valuable insights into advanced Python usage and computer programming
  principles.

### Docker

Docker and Docker Compose are fundamental components within the **sugar**
project infrastructure. These technologies facilitate the creation, deployment,
and management of isolated environments, making them integral to development and
testing processes in **sugar**.

To gain a foundational understanding of Docker and Docker Compose, consider
exploring the following tutorial, which provides a comprehensive introduction to
both technologies:
[Educative: Docker Compose Tutorial](https://www.educative.io/blog/docker-compose-tutorial).
This resource is designed to help newcomers grasp the essentials of Docker and
Docker Compose, covering everything from basic concepts to advanced usage
scenarios.

A thorough comprehension of Docker and Docker Compose is crucial for
contributing to the **sugar** project, as all development and deployment
workflows are designed around these technologies.

### How to Get Support

Should you require assistance, please join our community on the Open Science
Labs Discord server at
[https://opensciencelabs.org/discord](https://opensciencelabs.org/discord).
Here, you can participate in the incubator program and ask questions about Sugar
in its dedicated channel. You are also welcome to explore and join other groups
that align with your interests.

## Setting Up for Local Development

To contribute to `sugar`, follow these steps to set up your development
environment:

1. **Fork the Repository**: Begin by forking the `sugar` repository on GitHub to
   your own account.

2. **Clone Your Fork Locally**: Clone the forked repository to your local
   machine and navigate into the project directory.

   ```bash
   $ git clone git@github.com:your_username/sugar.git
   $ cd sugar
   ```

3. **Install Dependencies**: Use `mamba` to create a Conda environment and
   `poetry` for managing Python dependencies.

   ```bash
   $ mamba env create --file conda/dev.yaml --force
   $ poetry config virtualenvs.create false
   $ poetry install
   ```

4. **Create a Development Branch**: Make a dedicated branch for your bugfix or
   feature.

   ```bash
   $ git checkout -b name-of-your-bugfix-or-feature
   ```

5. **Make Changes Locally**: You are now ready to implement your changes or
   improvements.

6. **Install and Use Pre-commit Hooks**: `sugar` utilizes `pre-commit` hooks to
   ensure code quality. Install them locally and they will automatically run on
   each commit.

   ```bash
   $ pre-commit install
   $ pre-commit run --all-files
   ```

   To bypass the hooks temporarily, use `git commit` with `--no-verify`.

7. **Run Smoke Tests**: Quickly validate the functionality of your changes with
   smoke tests.

   ```bash
   $ makim tests.smoke
   ```

   Always complement smoke tests with thorough unit testing to ensure code
   integrity.

8. **Unit Testing with `pytest`**: `sugar` leverages `pytest` for unit testing,
   along with `pytest-cov` for coverage analysis. Run unit tests using:

   ```bash
   $ python -m pytest
   ```

   or

   ```bash
   $ makim tests.unittest
   ```

9. **Commit and Push Changes**: Stage, commit, and push your changes to GitHub.
   After setting the upstream branch once, subsequent pushes only require
   `git push`.

   ```bash
   $ git add .
   $ git commit -m "Detailed description of your changes."
   $ git push --set-upstream origin <branch name>
   ```

10. **Submit a Pull Request**: Once your changes are pushed, go to the GitHub
    website to submit a pull request for review.

## Release Process

The **Sugar** project utilizes `semantic-release` to automate the release
process, basing new releases on the content of commit messages.

### Commit Message Format

`semantic-release` analyzes commit messages to assess the impact of changes made
to the codebase. Adhering to a standardized commit message format allows
`semantic-release` to automatically determine the next semantic version number,
generate a comprehensive changelog, and publish the release.

While `semantic-release` defaults to the
[Angular Commit Message Conventions](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-format),
**Sugar** adopts the "Conventional Commits" standard
([https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/)).
This standard facilitates more detailed commit messages, especially for
"breaking changes".

Given the project's use of the `squash and merge` strategy for merging pull
requests, it is crucial to format the PR title according to the commit message
standards.

To aid contributors in crafting compliant commit messages, tools like
[commitizen](https://github.com/commitizen/cz-cli) and
[commitlint](https://github.com/conventional-changelog/commitlint) are
recommended. These tools help ensure that commit messages adhere to the required
format.

The following table illustrates how different commit messages correspond to the
type of release generated by `semantic-release`, according to its default
configuration:

| Commit Message Example                                       | Release Type  |
| ------------------------------------------------------------ | ------------- |
| `fix(pencil): stop graphite breaking when too much pressure` | Patch Release |
| `feat(pencil): add 'graphiteWidth' option`                   | Minor Release |
| `perf(pencil): optimize 'graphiteWidth' calculation`         | Patch Release |
| `fix(pencil)!: 'graphiteWidth' option removed`               | Major Release |

**Note**: Within the Conventional Commits standard, appending `!` to the message
prefix indicates a breaking change.

For more details on the commit message format used by `semantic-release`, visit
the
[semantic-release documentation](https://github.com/semantic-release/semantic-release#commit-message-format).
