# DevOps Course - Complete Learning Repository

Welcome to the comprehensive DevOps october course repository! This repository contains all lesson summaries, hands-on labs, and supplementary materials to guide you through your DevOps journey.


## Learning Objectives

By the end of this course, you will be able to:

- Understand core DevOps principles and culture
- Implement CI/CD pipelines using industry-standard tools
- Manage infrastructure as code (IaC)
- Containerize applications using Docker and orchestrate with Kubernetes
- Monitor and log applications effectively
- Collaborate effectively using version control and agile methodologies

## 📂 Repository Structure

```
devops-course/
├── README.md
├── Docker/
│   ├── lessons/
│   │   ├── lesson1.md
│   │   ├── lesson2.md
│   │   └── lesson3.md
│   ├── labs/
│   │   ├── lab1.md
│   │   ├── lab2.md
│   │   └── lab3.md
│   ├── pdf/
│   │   ├── lesson1.pdf
│   │   └── lesson2.pdf
│   └── ... (additional lessons)
├── k8s/
│   ├── lessons/
│   │   ├── lesson1.md
│   │   ├── lesson2.md
│   │   └── lesson3.md
│   ├── labs/
│   │   ├── lab1.md
│   │   ├── lab2.md
│   │   └── lab3.md
│   ├── pdf/
│   │   ├── lesson1.pdf
│   │   └── lesson2.pdf
│   └── ... (additional lessons)
└── ... (additional lessons)
```

## 📖 Course Curriculum

### Module 1: DevOps Foundations
- Version Control with Git
  - Git fundamentals and workflows
  - Branching strategies
  - Collaboration with GitHub/GitLab


### Module 2: Continuous Integration & Continuous Deployment
- CI/CD Fundamentals
  - Understanding CI/CD pipelines
  - Benefits and best practices

- Jenkins for CI/CD
  - Jenkins installation and configuration
  - Creating and managing pipelines
  - Jenkins plugins ecosystem

### Module 3: Containerization
- Docker Fundamentals
  - Introduction to containers
  - Docker images and containers
  - Dockerfile best practices

- Docker Compose
  - Multi-container applications
  - Docker networking and volumes

- Container Registries
  - Docker Hub, AWS ECR, Azure ACR
  - Managing and securing container images


### Module 4: Container Orchestration
- Kubernetes Fundamentals
  - Kubernetes architecture
  - Pods, deployments, and services


- Kubernetes Advanced Concepts
  - ConfigMaps and Secrets
  - Persistent volumes
  - Helm package manager


### Module 5: Infrastructure as Code
- Introduction to IaC
  - IaC principles and benefits
  - Declarative vs imperative approaches

- Terraform
  - Terraform basics
  - Providers, resources, and modules
  - State management

### Module 7: Monitoring & Logging
- Monitoring with Prometheus
  - Metrics collection
  - PromQL queries

- Visualization with Grafana
  - Creating dashboards
  - Alerting
  - [Summary](lessons/lesson-17-grafana/summary.md) | [Lab](lessons/lesson-17-grafana/lab.md) | [PDF](lessons/lesson-17-grafana/slides.pdf)

## Prerequisites

- Basic understanding of Linux/Unix command line
- Familiarity with at least one programming language
- Understanding of web applications and networking basics
- A computer with at least 8GB RAM (16GB recommended for running VMs and containers)

## Required Tools

Before starting the course, ensure you have the following tools installed:

- Git
- Docker 
- A code editor (VS Code recommended)
- Virtual machine software (VirtualBox or VMware)
- Cloud account (AWS Free Tier, Azure Free Trial, or GCP Free Trial)

Installation guides are available in the [resources/tools-installation](resources/tools-installation/) directory.

## Getting Started

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/devops-course.git
   cd devops-course
   ```

2. **Navigate to Lesson 1**
   ```bash
   cd lessons/lesson-01-introduction-to-devops
   ```

3. **Read the lesson summary**
   - Open `summary.md` to understand the concepts
   - Review the `slides.pdf` for visual explanations

4. **Complete the lab**
   - Follow the instructions in `lab.md`
   - Practice hands-on exercises
   - Check your understanding with lab questions

5. **Move to the next lesson**
   - Progress sequentially through the modules
   - Complete all labs before moving forward


## Additional Resources

- **Cheat Sheets**: Quick reference guides for commands and concepts
- **Additional Reading**: Links to documentation, blog posts, and tutorials
- **Video Tutorials**: Supplementary video content
- **Community Forum**: Discussion board for questions and collaboration

## Projects

### Mini Projects
Throughout the course, you'll complete several mini-projects to reinforce your learning:
- Automated deployment pipeline
- Containerized microservices application
- Infrastructure provisioning with Terraform
- Complete monitoring solution

### Final Project
Apply everything you've learned by building and deploying a complete application with:
- Version-controlled codebase
- CI/CD pipeline
- Containerized architecture
- Kubernetes orchestration
- Infrastructure as code
- Monitoring and logging
- Security best practices
