# Jenkins Pipeline: Parameters

## What Are Pipeline Parameters?

Parameters allow you to pass input values to a pipeline at runtime. Instead of hardcoding values, you can prompt users to provide information when they trigger a build.

Think of parameters as questions your pipeline asks before it starts running.

## Why Use Parameters?

### Flexibility

Without parameters:
- Pipeline always does the same thing
- Different behaviors require different pipelines
- Changes require code modifications

With parameters:
- One pipeline handles multiple scenarios
- Users choose options at runtime
- No code changes for different inputs

### Common Use Cases

| Use Case | Example Parameter |
|----------|-------------------|
| Choose environment | dev, staging, prod |
| Select version | 1.0.0, 1.1.0, latest |
| Toggle features | Run tests? Yes/No |
| Specify target | Server IP, bucket name |
| Control behavior | Clean build? Full deploy? |
| Input credentials | API key, username |

## Parameter Types

### String Parameter

**What it is:** A single-line text input field.

**Use for:**
- Version numbers
- Branch names
- Server addresses
- Simple text values

**Characteristics:**
- Free-form text entry
- Can have default value
- No validation by default
- Single line only

### Text Parameter

**What it is:** A multi-line text input area.

**Use for:**
- Commit messages
- Configuration blocks
- Multiple values (one per line)
- JSON/YAML snippets

**Characteristics:**
- Multiple lines allowed
- Larger input area
- Good for complex input
- No formatting

### Boolean Parameter

**What it is:** A checkbox that represents true/false.

**Use for:**
- Feature toggles
- Skip options
- Enable/disable behaviors
- Yes/No decisions

**Characteristics:**
- Simple checkbox UI
- Returns true or false
- Clear binary choice
- Has default state

**Common Boolean Parameters:**

| Parameter | Purpose |
|-----------|---------|
| SKIP_TESTS | Skip test execution |
| CLEAN_BUILD | Delete workspace first |
| DEPLOY | Actually deploy or dry-run |
| NOTIFY | Send notifications |
| DEBUG | Enable verbose logging |

### Choice Parameter

**What it is:** A dropdown menu with predefined options.

**Use for:**
- Environment selection
- Predefined versions
- Limited valid options
- Controlled choices

**Characteristics:**
- User picks from list
- First option is default
- Prevents invalid input
- Clear available options

**Common Choice Parameters:**

| Parameter | Options |
|-----------|---------|
| ENVIRONMENT | dev, staging, production |
| REGION | us-east-1, eu-west-1, ap-south-1 |
| BUILD_TYPE | debug, release |
| BRANCH | main, develop, release |

### Password Parameter

**What it is:** A masked text input for sensitive values.

**Use for:**
- API keys
- Tokens
- Passwords
- Secrets

**Characteristics:**
- Input is masked (dots/asterisks)
- Value hidden in logs (usually)
- Not stored in build history
- Use credentials plugin for better security

**Important:** Password parameters are not truly secure. For real secrets, use the Credentials plugin.

### File Parameter

**What it is:** A file upload input.

**Use for:**
- Configuration files
- Certificates
- Data files
- Custom scripts

**Characteristics:**
- User uploads file
- File saved to workspace
- Available during build
- Deleted after build (usually)

### Run Parameter

**What it is:** Select a previous build from another job.

**Use for:**
- Promoting builds
- Deploying specific versions
- Referencing artifacts
- Pipeline chains

**Characteristics:**
- Lists builds from specified job
- Can filter by status
- Provides build number
- Links pipelines together

## Parameter Behavior

### Build With Parameters

When a pipeline has parameters:
1. "Build Now" becomes "Build with Parameters"
2. User sees a form with all parameters
3. User fills in values or accepts defaults
4. Build starts with provided values

### First Build Issue

**The Problem:** The first build doesn't know about parameters yet.

**Why:** Jenkins discovers parameters by running the pipeline once.

**Solution Options:**
- Run first build to register parameters
- Pre-define parameters in job config
- Accept that first build may fail

### Default Values

Every parameter should have a sensible default:

| Parameter Type | Default Strategy |
|----------------|------------------|
| String | Most common value |
| Boolean | Safest option (usually false) |
| Choice | Most frequently used option |
| Password | Empty (require input) |

## Accessing Parameters

### In Pipeline Steps

Parameters become available as variables:
- Use the parameter name directly
- Access via `params.PARAMETER_NAME`
- Available in all stages

### Variable Types

| Parameter Type | Variable Type |
|----------------|---------------|
| String | String |
| Text | String |
| Boolean | Boolean (true/false) |
| Choice | String |
| Password | String (masked) |
| File | File path |

## Parameter Validation

### Built-in Validation

| Type | Validation |
|------|------------|
| Choice | Must be one of the options |
| Boolean | Must be true or false |
| String | None (any text allowed) |

### Custom Validation

You can add validation logic:
- Check format (regex)
- Verify value exists
- Validate against external system
- Fail early if invalid

### Common Validations

| Check | Purpose |
|-------|---------|
| Not empty | Required fields |
| Pattern match | Format validation |
| Exists check | Valid resource |
| Permission check | Authorization |

## Parameter Organization

### Grouping Parameters

For pipelines with many parameters:
- Group related parameters together
- Order by importance
- Use clear descriptions
- Consider hiding advanced options

### Parameter Descriptions

Good descriptions include:
- What the parameter controls
- Valid values or format
- Default behavior
- Example values

### Naming Conventions

| Style | Example | Use Case |
|-------|---------|----------|
| UPPER_SNAKE | DEPLOY_ENV | Traditional Jenkins |
| lowerCamel | deployEnv | Modern preference |
| Descriptive | TARGET_ENVIRONMENT | Self-documenting |

## Pipeline Flow with Parameters

```
┌─────────────────────────────────────────┐
│         User Clicks "Build"             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     Parameter Form Displayed            │
│  ┌─────────────────────────────────┐    │
│  │ Environment: [dropdown]         │    │
│  │ Version: [text field]           │    │
│  │ Run Tests: [checkbox]           │    │
│  │ Deploy: [checkbox]              │    │
│  └─────────────────────────────────┘    │
│              [Build] [Cancel]           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Parameters Passed to Pipeline      │
│                                         │
│   params.ENVIRONMENT = "staging"        │
│   params.VERSION = "1.2.3"              │
│   params.RUN_TESTS = true               │
│   params.DEPLOY = false                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Pipeline Uses Parameter Values     │
│                                         │
│   - Conditional stages based on params  │
│   - Pass values to scripts              │
│   - Configure deployments               │
└─────────────────────────────────────────┘
```

## Common Parameter Patterns

### Environment Selection

| Parameter | Type | Options |
|-----------|------|---------|
| ENVIRONMENT | Choice | dev, staging, prod |

**Controls:** Where code is deployed, which configs are used.

### Version Selection

| Approach | When to Use |
|----------|-------------|
| Free text | Any version allowed |
| Choice | Limited known versions |
| Run parameter | Pick from previous builds |

### Feature Flags

| Parameter | Default | Purpose |
|-----------|---------|---------|
| SKIP_TESTS | false | Speed up builds |
| CLEAN_WORKSPACE | false | Fresh builds |
| DRY_RUN | true | Safe default |
| DEBUG_MODE | false | Extra logging |

### Approval Gates

| Parameter | Type | Purpose |
|-----------|------|---------|
| APPROVED_BY | String | Who authorized |
| CHANGE_TICKET | String | Reference number |
| CONFIRM_PRODUCTION | Boolean | Extra confirmation |

## Parameters vs Other Input Methods

| Method | When to Use |
|--------|-------------|
| Parameters | User input at build time |
| Environment Variables | System/agent configuration |
| Credentials | Secrets and sensitive data |
| Properties Files | Static configuration |
| External Systems | Dynamic lookups |

## Best Practices

| Practice | Reason |
|----------|--------|
| Provide defaults | Builds work without input |
| Use Choice when possible | Prevent invalid values |
| Write clear descriptions | Users understand options |
| Validate early | Fail fast on bad input |
| Limit parameters | Too many is overwhelming |
| Use Boolean for toggles | Clear yes/no choices |
| Avoid passwords | Use Credentials plugin |
| Group logically | Easy to understand |
| Name consistently | Predictable patterns |
| Document parameters | In README or wiki |

## Security Considerations

| Concern | Recommendation |
|---------|----------------|
| Sensitive values | Use Credentials, not Password param |
| User input | Validate and sanitize |
| Command injection | Don't pass params directly to shell |
| Audit trail | Parameters are logged |
| Access control | Limit who can build with params |
