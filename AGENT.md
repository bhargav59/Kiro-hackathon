# AGENT.md - Universal AI Coding Agent Configuration

> **Philosophy**: This setup is intentionally vanilla and works great out of the box. There's no one correct way to use AI coding agents - customize and hack it however you like. Each developer uses it very differently.

> **Tool Agnostic**: This configuration works with any AI coding CLI tool like `kiro-cli`, `gemini-cli`, `aider`, `cursor`, or similar tools that provide terminal-based AI assistance.

---

## Core Principles

1. **Always give the agent a way to verify its work** - If the agent has a feedback loop, it will 2-3x the quality of the final result
2. **Use Plan mode first** - Get the plan right before executing
3. **Automate common workflows** - Save repeated prompting with commands and subagents
4. **Share learnings with the team** - Document mistakes and best practices

---

## Development Workflow

### Always use `bun`, not `npm`

**Key Commands:**
```bash
# 1. Make changes

# 2. Typecheck (fast)
bun run typecheck

# 3. Run tests
bun run test -- -t "test name"           # Single suite
bun run test:file -- "glob"              # Specific files

# 4. Lint before committing
bun run lint:file -- "file1.ts"          # Specific files
bun run lint                              # All files

# 5. Before creating PR
bun run lint:ai && bun run test
```

---

## Model & Strategy

### Primary Model: Reasoning Model with Extended Thinking

**Why Use Reasoning Models:**
- Best coding results available
- Even though they're bigger & slower than lighter models
- Requires less steering and better at tool use
- Almost always faster than using a lighter model in the end
- Better at understanding complex codebases and architectural decisions

**Model Selection Strategy:**
- **Reasoning models** (e.g., o1, extended thinking models): For complex tasks, architectural decisions, debugging tricky issues
- **Lighter models** (e.g., fast models, smaller context): For simple edits, formatting, quick iterations

**Key Setting:** Always enable **Extended Thinking/Reasoning** mode for maximum quality on complex tasks

---

## Session Management

### Parallel Workflows

**1/ Terminal Sessions (5 parallel AI agents)**
- Number tabs 1-5 in your terminal
- Use system notifications to know when an agent needs input
- Works with any CLI tool: `kiro-cli`, `gemini-cli`, `aider`, etc.
- Example: Run `kiro-cli` in tab 1, `gemini-cli` in tab 2, etc.

**2/ Web Sessions (5-10 parallel on various platforms)**
- Run in parallel with local terminal sessions
- Use web interfaces: claude.ai, chatgpt.com, gemini.google.com, etc.
- Handoff local sessions to web when needed
- Start sessions from phone throughout the day and check in later

**3/ Session Organization**
- Start with a clear plan before executing code
- Write PR goal and overall strategy first
- Go back and forth with the AI until plan is solid
- Then switch to execution mode for implementation
- Use auto-accept/fast mode once you trust the plan

**Tool-Specific Commands:**
```bash
# kiro-cli examples
kiro-cli --model reasoning    # Use reasoning model
kiro-cli --model fast         # Use lighter/faster model

# gemini-cli examples  
gemini-cli --thinking         # Enable extended thinking
gemini-cli --quick            # Quick responses

# aider examples
aider --opus                  # Use reasoning model
aider --sonnet                # Use lighter model
```

---

## Team Collaboration

### Shared AGENT.md File

**Location:** `./AGENT.md` in the repository root

**Purpose:**
- Checked into git
- Whole team contributes multiple times a week
- When AI does something incorrectly, add it to AGENT.md
- AI learns not to repeat mistakes
- Works with any AI coding tool that can read project files

**Example Content:**
```markdown
# Development Workflow

**Always use `bun`, not `npm`.**

## Code Style

- Prefer `type` over `interface`; avoid `enum` (use string unions)
- **Never use `enum`** (use string literal unions instead)

## Common Patterns

[Add your team's specific patterns here]

## AI Guidance

- Always run tests after changes
- Use reasoning models for architecture decisions
- Use lighter models for simple formatting tasks
```

**Note:** Other teams maintain their own AGENT.md files. It's each team's job to keep theirs up to date.

---

## Code Review Integration

### Tag AI Bot on PRs (Optional)

**Setup Options:**
- GitHub Actions that trigger AI review
- Manual review using your preferred AI tool
- Integration bots if available for your tool

**Purpose:** 
- Add learnings to AGENT.md as part of the PR
- During code review, document patterns for AI to learn
- Improve AI performance over time through feedback

**Example Manual Workflow:**
```
Developer: "nit: use a string literal, not ts enum"
Action: Update AGENT.md with the guidance

Add to AGENT.md:
- Prefer `type` over `interface`; **never use `enum`** (use string literal unions instead)

Commit: "docs: update AGENT.md - prefer string literals over enums"
```

**Alternative:** Use AI to help update AGENT.md
```bash
# Using kiro-cli
kiro-cli "Read the PR feedback and update AGENT.md to document this pattern"

# Using gemini-cli  
gemini-cli "Add this coding guideline to AGENT.md: never use TypeScript enums"
```

---

## Custom Commands & Automation

### Shell Aliases and Scripts

**Purpose:** Save repeated prompting for "inner loop" workflows done many times daily

**Location:** `~/.bashrc`, `~/.zshrc`, or project-specific scripts

**Example Aliases:**
```bash
# ~/.zshrc or ~/.bashrc
alias ai-commit='kiro-cli "create a commit message and push"'
alias ai-pr='kiro-cli "create a PR with good title and description"'
alias ai-fix='gemini-cli "fix linting and formatting issues"'
alias ai-test='kiro-cli "write tests for the changes I just made"'

# Project-specific script: scripts/ai-workflow.sh
#!/bin/bash
# Commit, push, and open a PR with AI assistance

echo "Running pre-commit checks..."
bun run lint && bun run test

if [ $? -eq 0 ]; then
    echo "Creating commit and PR with AI..."
    kiro-cli --model reasoning "Analyze git diff, create semantic commit message, push, and create PR"
else
    echo "Tests failed. Fix issues first."
fi
```

**Tool-Specific Command Patterns:**

```bash
# kiro-cli with file context
kiro-cli --files "src/**/*.ts" "refactor these files to use the new pattern"

# gemini-cli with specific instructions
gemini-cli --system "You are a senior developer doing code review" "review my changes"

# aider with architect mode
aider --architect "plan the implementation of feature X"
```

---

## Prompt Templates & Reusable Instructions

**Purpose:** Automate the most common workflows for PRs

**Location:** `.ai-prompts/` or `docs/ai-prompts/` in your repo

**Common Templates:**

### `code-simplifier.md`
```markdown
# Code Simplifier Prompt

Review the code and simplify it:
- Remove unnecessary complexity
- Consolidate duplicate logic
- Improve variable names for clarity
- Remove dead code
- Optimize imports

Maintain all functionality and tests must still pass.
```

### `verify-app.md`
```markdown
# Application Verification Prompt

Test the application end-to-end:
1. Run all tests: `bun test`
2. Check types: `bun run typecheck`
3. Lint code: `bun run lint`
4. Build project: `bun run build`
5. Start dev server and test manually
6. Check for console errors
7. Verify all features work as expected

Report any issues found.
```

### `build-validator.md`
```markdown
# Build Validation Prompt

Validate the build:
- Ensure all dependencies are installed
- Check for TypeScript errors
- Verify build completes successfully
- Check bundle size hasn't increased significantly
- Ensure no build warnings
```

### `code-architect.md`
```markdown
# Code Architecture Prompt

Plan the architecture for this feature:
1. Analyze requirements
2. Identify components/modules needed
3. Define interfaces and contracts
4. Plan data flow
5. Consider error handling
6. Identify potential edge cases
7. Suggest testing strategy

Provide a detailed implementation plan before writing code.
```

### `oncall-guide.md`
```markdown
# Oncall Incident Response Prompt

When investigating an incident:
1. Check error logs and metrics
2. Identify the scope of impact
3. Find the root cause
4. Propose immediate fix
5. Create rollback plan if needed
6. Document incident timeline
7. Suggest preventive measures
```

**Usage:**
```bash
# Using templates with kiro-cli
cat .ai-prompts/code-simplifier.md | kiro-cli

# Using with gemini-cli
gemini-cli --file .ai-prompts/verify-app.md "apply this to the current codebase"

# Combining template with specific context
cat .ai-prompts/code-architect.md | kiro-cli "$(cat docs/new-feature.md)"
```

---

## Code Formatting

### Git Hooks for Auto-Formatting

**Setup with Husky:**
```bash
# Install husky
bun add -D husky

# Initialize git hooks
bunx husky init

# Create pre-commit hook: .husky/pre-commit
#!/bin/sh
bun run format || true
bun run lint:staged
```

**Alternative: Manual formatting script**
```bash
# scripts/format-changed.sh
#!/bin/bash
# Format only changed files

git diff --name-only --cached | grep -E '\.(ts|tsx|js|jsx)$' | while read file; do
    bun run format "$file" || true
done
```

**Purpose:**
- AI tools usually generate well-formatted code
- Hooks handle the last 10% to avoid formatting errors in CI
- Runs automatically on commit or file save

**Integration with AI tools:**
```bash
# kiro-cli with auto-format
kiro-cli "make changes" && bun run format

# Watch mode with formatting
ls src/**/*.ts | entr -c sh -c 'kiro-cli --continue && bun run format'
```

---

## Safety & Permissions Management

### Safe Command Practices

**Principle:** Pre-approve safe, read-only commands; review destructive ones

**Common Safe Commands (Tool-Agnostic):**
```bash
# Read-only operations (generally safe)
git status, git log, git diff
cat, less, head, tail, grep
ls, find, tree
bun run test, bun run build
npm test, npm run build
docker ps, docker logs

# Destructive operations (require review)
rm -rf, git push --force
docker rm, docker system prune
npm publish, bun publish
```

**Tool-Specific Safety:**

**kiro-cli / gemini-cli:**
```bash
# Review mode (asks before executing)
kiro-cli --confirm "make changes to database migration"

# Dry-run mode
kiro-cli --dry-run "generate deployment config"

# Safe mode (no file writes)
kiro-cli --read-only "analyze the codebase"
```

**Environment-Based Permissions:**
```bash
# Development: Allow most operations
export AI_TOOL_ENV=development

# Production: Require explicit confirmation
export AI_TOOL_ENV=production
export AI_REQUIRE_CONFIRMATION=true
```

**Best Practices:**
1. Use version control - always commit before AI makes changes
2. Review diffs before accepting changes
3. Test in development before production
4. Use read-only mode for analysis tasks
5. Keep destructive operations manual
6. Document approved commands in AGENT.md

---

## Tool Integration

### Connecting AI to Your Development Tools

**Common Integration Patterns:**

**1. API Access via Environment Variables**
```bash
# ~/.bashrc or ~/.zshrc
export SLACK_TOKEN="xoxb-..."
export JIRA_TOKEN="..."
export GITHUB_TOKEN="ghp_..."
export SENTRY_TOKEN="..."

# AI tools can access these when needed
kiro-cli "check our Slack for latest deployment status"
gemini-cli "create a Jira ticket for this bug"
```

**2. CLI Tool Integration**
```bash
# Install CLI tools the AI can use
brew install gh          # GitHub CLI
brew install slack-cli   # Slack CLI  
npm install -g jira-cli  # Jira CLI

# AI can now use these tools
kiro-cli "use gh cli to create a PR"
gemini-cli "use slack-cli to post update to #engineering"
```

**3. Custom Scripts as Interfaces**
```bash
# scripts/query-analytics.sh
#!/bin/bash
# Wrapper for BigQuery that AI can use safely
bq query --use_legacy_sql=false "$1"

# scripts/check-logs.sh
#!/bin/bash
# Safe log access
docker logs "$1" --tail=100

# AI usage
kiro-cli "use scripts/query-analytics.sh to check daily active users"
```

**4. Configuration Files**
```json
// .ai-tools-config.json
{
  "tools": {
    "slack": {
      "enabled": true,
      "channels": ["#engineering", "#deploys"]
    },
    "github": {
      "enabled": true,
      "repo": "org/repo"
    },
    "monitoring": {
      "sentry_project": "myapp",
      "datadog_dashboard": "production"
    }
  }
}
```

**Purpose:** Let AI access your team's tools without manual intervention

**Safety Note:** Only give AI access to tools with appropriate read/write permissions

---

## Long-Running Tasks

### Background Execution Strategies

**Options for tasks that take hours:**

**1. Run in tmux/screen session**
```bash
# Start tmux session
tmux new -s ai-task

# Run long task
kiro-cli --model reasoning "refactor entire codebase to new architecture"

# Detach: Ctrl+B, then D
# Reattach later: tmux attach -t ai-task
```

**2. Use background processes with logging**
```bash
# Run in background with output logging
nohup kiro-cli "complex-task" > ai-output.log 2>&1 &

# Check progress
tail -f ai-output.log

# Check if still running
ps aux | grep kiro-cli
```

**3. Break into smaller tasks**
```bash
# Instead of one huge task, break it down
kiro-cli "Step 1: Plan the refactoring" > plan.md
kiro-cli "Step 2: Refactor module A using plan.md"
kiro-cli "Step 3: Refactor module B using plan.md"
# etc.
```

**4. Scheduled verification**
```bash
# scripts/verify-after-completion.sh
#!/bin/bash
# Wait for AI to finish, then verify

while pgrep -f "kiro-cli" > /dev/null; do
    echo "AI still working..."
    sleep 60
done

echo "AI finished. Running verification..."
bun run test
bun run lint
echo "Verification complete!"
```

**5. Interactive mode with checkpoints**
```bash
# Use interactive mode for long tasks
kiro-cli --interactive

# AI will pause at checkpoints
> Working on phase 1... (done, continue? y/n)
> Working on phase 2... (done, continue? y/n)
```

**Safety for Unattended Tasks:**
- Always use version control
- Commit before starting long tasks
- Use `--dry-run` mode first if available
- Set up notification alerts (email, Slack) when done
- Review all changes carefully afterward

---

## Verification & Testing

### Critical: Give AI a Verification Method

**Why:** This is the single most important thing for quality results

**Examples by domain:**

#### Web Applications
```bash
# Manual verification prompt
kiro-cli "Make the changes, then I'll test in browser"

# Automated verification
kiro-cli "Make changes and verify they work by:
1. Running the dev server
2. Opening http://localhost:3000
3. Testing the feature manually
4. Checking console for errors
Report any issues found"
```

#### Command Line Tools
```bash
gemini-cli "Implement the feature and verify it works by:
1. Running the command with test inputs
2. Checking the output is correct
3. Testing edge cases
4. Running the test suite"
```

#### Libraries with Test Suites
```bash
kiro-cli "Make changes and verify by:
1. Running: bun test
2. Ensure all tests pass
3. Add new tests if needed
4. Run: bun run typecheck
Report results"
```

#### Mobile Apps
```bash
gemini-cli "Implement and verify by:
1. Building the app
2. Running in iOS simulator / Android emulator
3. Testing the feature manually
4. Checking for console errors
Report any issues"
```

**Setup:** Create a verification template in `.ai-prompts/verify-app.md`

**Automated Verification Script:**
```bash
# scripts/ai-verify.sh
#!/bin/bash
# Comprehensive verification after AI changes

echo "Running verification suite..."

# 1. Type checking
echo "✓ Checking types..."
bun run typecheck || exit 1

# 2. Linting
echo "✓ Linting..."
bun run lint || exit 1

# 3. Tests
echo "✓ Running tests..."
bun test || exit 1

# 4. Build
echo "✓ Building..."
bun run build || exit 1

# 5. Check bundle size
echo "✓ Checking bundle size..."
bun run bundle-size

echo "✅ All verifications passed!"
```

**Usage:**
```bash
# After AI makes changes
kiro-cli "implement feature X"
./scripts/ai-verify.sh

# Or include in AI prompt
kiro-cli "implement feature X, then run ./scripts/ai-verify.sh and report results"
```

---

## Multiple Display Setup

### Workspace Organization

**Purpose:** Keep parallel sessions visible and manageable

**Recommended Setup:**
- Use multiple displays for expansive workspace
- Keep parallel sessions visible simultaneously
- Monitor progress across multiple agents
- Quickly context-switch between sessions

---

## Advanced Configurations

### Tool-Specific Configuration Files

**kiro-cli configuration example:**
```json
// ~/.kiro-config.json
{
  "default_model": "reasoning",
  "context_files": ["AGENT.md", "README.md"],
  "auto_commit": false,
  "confirm_before_write": true
}
```

**gemini-cli configuration example:**
```json
// ~/.gemini-config.json
{
  "model": "gemini-2.0-flash-thinking-exp",
  "temperature": 0.7,
  "include_files": [".ai-prompts/**/*.md"]
}
```

**aider configuration example:**
```yaml
# .aider.conf.yml
model: gpt-4
edit-format: diff
auto-commits: false
dirty-commits: false
```

### Environment-Based Settings

```bash
# Development environment
export AI_ENV=development
export AI_AUTO_TEST=true
export AI_VERBOSE=true

# Production environment  
export AI_ENV=production
export AI_AUTO_TEST=false
export AI_REQUIRE_REVIEW=true
```

### Project-Specific AI Configuration

**Create `.aiconfig` in project root:**
```bash
# .aiconfig
# Project-specific AI tool configuration

# Always include these files for context
CONTEXT_FILES="AGENT.md,README.md,package.json"

# Run these checks after changes
POST_CHANGE_CHECKS="bun run typecheck && bun run lint"

# Preferred model for this project
PREFERRED_MODEL="reasoning"

# Auto-format after changes
AUTO_FORMAT=true
```

**Usage:**
```bash
# Source config before using AI tools
source .aiconfig

# Or create wrapper script: scripts/ai
#!/bin/bash
source .aiconfig
kiro-cli "$@"
```

---

## Documentation & Learning

### Consult Tool Documentation

**Key Resources by Tool:**

**kiro-cli:**
- Official docs (check tool's GitHub/website)
- Community examples and configs
- API documentation for available models

**gemini-cli:**
- Google AI documentation
- Model capabilities and limits
- Best practices guides

**aider:**
- `aider --help` for all options
- GitHub repository for examples
- Community cookbook

**General AI Coding Resources:**
- Tool-specific Discord/Slack communities
- GitHub discussions and issues
- Blog posts and tutorials from practitioners

**Stay Current:**
- Follow tool maintainers on social media
- Subscribe to release notes
- Join community forums
- Experiment with new features
- Share your learnings with the team

**Build Your Knowledge Base:**
- Document what works in AGENT.md
- Create prompt templates for common tasks
- Share configs with team
- Iterate on your workflow
- There is no wrong way - just your way!

---

## Getting Started Checklist

- [ ] Choose your AI coding tools (kiro-cli, gemini-cli, aider, etc.)
- [ ] Set up parallel terminal sessions (5 tabs numbered 1-5)
- [ ] Configure 5-10 web sessions on AI platforms (claude.ai, chatgpt.com, gemini, etc.)
- [ ] Create team's `AGENT.md` file in repo root
- [ ] Document safe commands and workflows in AGENT.md
- [ ] Create shell aliases for frequent workflows
- [ ] Build prompt templates for common tasks (in `.ai-prompts/`)
- [ ] Set up git hooks for auto-formatting (husky)
- [ ] Configure environment variables for tool access
- [ ] Create verification scripts (`scripts/ai-verify.sh`)
- [ ] Set up tmux/screen for long-running tasks
- [ ] Always use Plan mode/architecture mode before executing
- [ ] Enable Extended Thinking/Reasoning when available
- [ ] Create tool-specific config files
- [ ] Document your workflow in AGENT.md for the team

---

## Quick Reference

### Essential Commands
```bash
# Development workflow
bun run typecheck                    # Fast type checking
bun run test -- -t "test name"       # Run specific test
bun run lint:file -- "file.ts"       # Lint specific files
bun run lint:ai && bun run test      # Pre-PR validation

# AI tool usage examples
kiro-cli --model reasoning "complex task"     # Use reasoning model
kiro-cli --model fast "simple edit"           # Use lighter model
gemini-cli --thinking "architectural decision" # Enable thinking
gemini-cli --quick "format this file"         # Quick response

# Session management (tmux)
tmux new -s ai-session              # Start new session
tmux attach -t ai-session           # Reattach to session
# Ctrl+B, then D to detach

# Verification
./scripts/ai-verify.sh              # Run verification suite
bun run format && bun test          # Quick check

# Custom workflows  
ai-commit                           # Your custom alias
ai-pr                              # Create PR with AI
cat .ai-prompts/template.md | kiro-cli  # Use prompt template
```

### Essential AI Tool Flags
```bash
# kiro-cli
--model reasoning          # Best for complex tasks
--model fast              # Best for simple tasks
--confirm                 # Review before executing
--dry-run                 # Preview without changes
--files "src/**/*.ts"     # Include specific files
--continue                # Continue previous session

# gemini-cli
--thinking                # Enable extended thinking
--quick                   # Fast responses
--system "prompt"         # Set system prompt
--file path              # Include file context

# aider
--architect              # Architecture planning mode
--opus                   # Use best reasoning model
--sonnet                 # Use lighter model
--yes                    # Auto-accept changes
--no-auto-commits        # Manual commit control
```

### Key Principles
1. **Plan first** - Think through architecture before coding
2. **Verify always** - Give AI a way to check its work
3. **Automate repetition** - Use aliases and templates
4. **Share knowledge** - Update AGENT.md with learnings
5. **Stay flexible** - No single correct way, find yours!
6. **Use reasoning for complex** - Architecture, debugging, planning
7. **Use lighter for simple** - Formatting, small edits, quick fixes

---

## Philosophy & Approach

> "AI coding tools work great out of the box. Start simple, customize only when needed. There is no one correct way - each developer should find their own workflow that matches their style and needs."
>
> — Adapted from AI coding best practices

**Remember:** 
- Start simple with basic usage
- Add complexity only when you find pain points
- Share learnings with your team in AGENT.md
- Keep iterating on what works for you
- Build quality through verification loops
- Use reasoning models for complex work, lighter models for simple tasks
- Document your workflow so others can learn from it
- Experiment with different tools to find your fit
- The best workflow is the one that works for you!

**Tool Selection Tips:**
- **kiro-cli**: Great if you need access to multiple model providers
- **gemini-cli**: Excellent for fast iteration with Google's models
- **aider**: Strong for collaborative coding with git integration
- **cursor**: IDE integration for seamless workflow
- Try multiple tools - they each have strengths

---

*Last Updated: January 2026*
*Based on workflows from AI coding practitioners and adapted for universal use*
