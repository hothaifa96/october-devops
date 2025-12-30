# Jenkins Pipeline: Environment Variables

## What Are Environment Variables?

Environment variables are key-value pairs that provide configuration and context to your pipeline. They're available to all steps and can be used to customize behavior without changing code.

Think of them as global settings that your pipeline and the tools it runs can read.

## Why Environment Variables Matter

### Configuration Without Code Changes

Environment variables let you:
- Change behavior without editing the pipeline
- Use the same pipeline across environments
- Pass information between steps
- Configure external tools

### Standard Practice

Environment variables are the standard way to:
- Configure applications
- Pass secrets securely
- Identify the runtime environment
- Share data between processes

## Types of Environment Variables

### 1. Built-in Jenkins Variables

Jenkins automatically provides many useful variables.

#### Build Information

| Variable | Contains |
|----------|----------|
| BUILD_NUMBER | Current build number (1, 2, 3...) |
| BUILD_ID | Build identifier (same as BUILD_NUMBER for recent Jenkins) |
| BUILD_DISPLAY_NAME | Display name (#1, #2, or custom) |
| BUILD_TAG | String like "jenkins-jobname-buildnumber" |
| BUILD_URL | Full URL to this build's page |

#### Job Information

| Variable | Contains |
|----------|----------|
| JOB_NAME | Name of the project/job |
| JOB_BASE_NAME | Short name without folder path |
| JOB_URL | Full URL to the job |

#### Executor Information

| Variable | Contains |
|----------|----------|
| EXECUTOR_NUMBER | Number of the executor running this build |
| NODE_NAME | Name of the agent/node |
| NODE_LABELS | Labels assigned to the node |
| WORKSPACE | Absolute path to the workspace |

#### Jenkins Information

| Variable | Contains |
|----------|----------|
| JENKINS_HOME | Jenkins installation directory |
| JENKINS_URL | Full URL to Jenkins |

#### Source Control (Git)

| Variable | Contains |
|----------|----------|
| GIT_COMMIT | Full commit hash |
| GIT_BRANCH | Branch name |
| GIT_URL | Repository URL |
| GIT_AUTHOR_NAME | Commit author |
| GIT_AUTHOR_EMAIL | Author's email |
| GIT_COMMITTER_NAME | Who committed |
| GIT_COMMITTER_EMAIL | Committer's email |
| CHANGE_ID | Pull request ID (if applicable) |
| CHANGE_URL | Pull request URL |
| CHANGE_TITLE | Pull request title |
| CHANGE_AUTHOR | PR author |
| CHANGE_BRANCH | Source branch of PR |
| CHANGE_TARGET | Target branch of PR |

### 2. Custom Pipeline Variables

Variables you define in your pipeline.

#### Scope Options

| Scope | Where Defined | Available |
|-------|---------------|-----------|
| Global | Top-level environment block | Entire pipeline |
| Stage | Stage-level environment block | That stage only |
| Step | Within a step | That step only |

#### Variable Types

| Type | Description |
|------|-------------|
| Static | Fixed value set in pipeline |
| Dynamic | Computed at runtime |
| Credential | Injected from credentials store |
| From File | Read from properties file |

### 3. System Environment Variables

Variables from the operating system and agent.

| Variable | Contains |
|----------|----------|
| HOME | User's home directory |
| PATH | Executable search path |
| USER | Current username |
| SHELL | Default shell |
| JAVA_HOME | Java installation path |
| TERM | Terminal type |

## Setting Environment Variables

### Where to Define

| Location | Use Case |
|----------|----------|
| Pipeline environment block | Global settings |
| Stage environment block | Stage-specific settings |
| withEnv step | Temporary within block |
| Jenkins system config | All pipelines on Jenkins |
| Agent/node config | Specific to that agent |

### Value Sources

| Source | Description |
|--------|-------------|
| Literal string | Hardcoded value |
| Other variable | Reference existing variable |
| Credentials | From Jenkins credentials |
| Computed | Result of expression |
| External | From file or API |

## Credentials as Environment Variables

### Why Use Credentials

| Method | Problem |
|--------|---------|
| Plain text in pipeline | Visible in code, logs |
| Password parameter | Not truly secure |
| Credentials binding | Secure, audited, managed |

### Credential Types

| Type | Use For | Variables Created |
|------|---------|-------------------|
| Username/Password | Basic auth | USR, PSW |
| Secret text | API keys, tokens | Single variable |
| Secret file | Certificates, key files | File path |
| SSH key | Git, server access | Key file path |
| Certificate | SSL/TLS | Cert and key files |

### How Credentials Work

1. Store credential in Jenkins securely
2. Reference credential ID in pipeline
3. Jenkins injects value at runtime
4. Value masked in logs
5. Value removed after build

### Credential Scoping

| Scope | Visibility |
|-------|------------|
| System | Jenkins internal use |
| Global | All jobs |
| Folder | Jobs in folder/subfolder |
| Job | Single job only |

## Environment Variable Behavior

### Availability

| Where | Access Method |
|-------|---------------|
| Groovy code | `env.VARIABLE_NAME` |
| Shell steps | `$VARIABLE_NAME` or `${VARIABLE_NAME}` |
| Windows batch | `%VARIABLE_NAME%` |
| String interpolation | `"${env.VARIABLE_NAME}"` |

### Inheritance

Variables flow down:
- Pipeline → Stage → Step
- Parent values available to children
- Children can override
- Overrides don't affect parent

### Masking

| Situation | Behavior |
|-----------|----------|
| Credential bound | Masked in logs |
| Regular variable | Visible in logs |
| Explicitly masked | Masked in logs |

## Common Patterns

### Application Configuration

| Variable | Purpose |
|----------|---------|
| APP_ENV | Environment identifier |
| LOG_LEVEL | Logging verbosity |
| API_URL | Backend service URL |
| FEATURE_FLAGS | Enable/disable features |

### Build Configuration

| Variable | Purpose |
|----------|---------|
| BUILD_VERSION | Version being built |
| BUILD_TYPE | debug/release |
| TARGET_PLATFORM | OS/architecture |
| PARALLEL_JOBS | Concurrent processes |

### Deployment Configuration

| Variable | Purpose |
|----------|---------|
| DEPLOY_TARGET | Server or cluster |
| DEPLOY_REGION | Geographic region |
| REPLICAS | Number of instances |
| ROLLOUT_STRATEGY | How to deploy |

### Cloud Provider

| Variable | Purpose |
|----------|---------|
| AWS_REGION | AWS region |
| AWS_ACCOUNT_ID | Account identifier |
| AZURE_SUBSCRIPTION | Azure subscription |
| GCP_PROJECT | Google Cloud project |

## Environment Variable Flow

```
┌─────────────────────────────────────────────────────────┐
│                   Jenkins System                         │
│              (System-wide variables)                     │
└─────────────────────┬───────────────────────────────────┘
                      │ inherited by
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   Agent/Node                             │
│              (Node-specific variables)                   │
└─────────────────────┬───────────────────────────────────┘
                      │ inherited by
                      ▼
┌─────────────────────────────────────────────────────────┐
│               Pipeline Environment                       │
│              (Global pipeline variables)                 │
│                                                          │
│   BUILD_VERSION = "1.0.0"                               │
│   DEPLOY_ENV = "staging"                                │
└─────────────────────┬───────────────────────────────────┘
                      │ inherited by
                      ▼
┌─────────────────────────────────────────────────────────┐
│               Stage Environment                          │
│              (Stage-specific variables)                  │
│                                                          │
│   BUILD_VERSION = "1.0.0"  (inherited)                  │
│   DEPLOY_ENV = "staging"   (inherited)                  │
│   DB_HOST = "staging-db"   (stage-specific)             │
└─────────────────────┬───────────────────────────────────┘
                      │ inherited by
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    Step                                  │
│              (All variables available)                   │
│                                                          │
│   Can read: BUILD_VERSION, DEPLOY_ENV, DB_HOST          │
│   Plus: BUILD_NUMBER, WORKSPACE, etc.                   │
└─────────────────────────────────────────────────────────┘
```

## Parameters vs Environment Variables

| Aspect | Parameters | Environment Variables |
|--------|------------|----------------------|
| Set by | User at build time | Pipeline or system |
| Purpose | User input | Configuration |
| Access | `params.NAME` | `env.NAME` |
| Modifiable | No (after build starts) | Yes (in pipeline) |
| Prompted | Yes (build form) | No |

### Converting Parameters to Env Vars

Common pattern:
1. Accept input via parameter
2. Set environment variable from parameter
3. Use environment variable in steps

**Why:** Environment variables work consistently in shell scripts.

## Debugging Environment Variables

### Viewing All Variables

Methods to see what's available:
- Print all environment variables
- Use Jenkins "Environment Variables" page
- Add printenv to shell step

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Variable empty | Not defined or scope issue | Check definition location |
| Wrong value | Override or typo | Print value to debug |
| Not expanding | Wrong syntax | Check shell vs Groovy syntax |
| Credential not working | Wrong binding | Verify credential ID |

### Syntax Differences

| Context | Syntax |
|---------|--------|
| Groovy interpolation | `"${env.VAR}"` |
| Shell (Linux/Mac) | `$VAR` or `${VAR}` |
| Batch (Windows) | `%VAR%` |
| PowerShell | `$env:VAR` |

## Security Considerations

### Do's

| Practice | Reason |
|----------|--------|
| Use credentials binding | Secure storage and masking |
| Limit credential scope | Principle of least privilege |
| Audit credential access | Track who uses what |
| Rotate credentials | Limit exposure window |

### Don'ts

| Practice | Risk |
|----------|------|
| Echo credentials | Visible in logs |
| Hardcode secrets | In version control |
| Wide credential scope | Unnecessary access |
| Share credentials | No accountability |

### Masked Variables

Masking prevents accidental exposure:
- Credential-bound variables auto-masked
- Can manually mask sensitive values
- Masked in console output
- Still present in memory/use

## Best Practices

| Practice | Benefit |
|----------|---------|
| Use meaningful names | Self-documenting |
| UPPER_CASE convention | Easy to identify |
| Set defaults | Works without configuration |
| Document variables | Others understand usage |
| Scope appropriately | Only where needed |
| Use credentials for secrets | Security |
| Don't echo sensitive values | Prevent leaks |
| Validate required variables | Fail fast |
| Group related variables | Organization |
| Use consistent patterns | Predictability |

## Quick Reference

### Jenkins Built-in Variables

| Category | Key Variables |
|----------|---------------|
| Build | BUILD_NUMBER, BUILD_URL |
| Job | JOB_NAME, JOB_URL |
| Workspace | WORKSPACE |
| Node | NODE_NAME, EXECUTOR_NUMBER |
| Git | GIT_COMMIT, GIT_BRANCH |
| PR | CHANGE_ID, CHANGE_BRANCH |

### Common Custom Variables

| Variable | Purpose |
|----------|---------|
| VERSION | Application version |
| ENVIRONMENT | Target environment |
| REGION | Geographic region |
| DEBUG | Enable debugging |
| DRY_RUN | Skip actual changes |

## Summary

Environment variables are fundamental to Jenkins pipelines:
- Built-in variables provide context
- Custom variables configure behavior
- Credentials provide secure secrets
- Proper scoping maintains organization
- Security requires careful handling

