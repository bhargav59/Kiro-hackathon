# CloudEngineered - Subagent Configuration

## Subagent Architecture Overview

CloudEngineered leverages Kiro CLI's subagent system for specialized task delegation and parallel processing. This document outlines the subagent configurations and usage patterns.

## Available Subagents

### 1. Data Enhancement Subagent
**Purpose**: Handle data enrichment tasks independently
**Specialization**: GitHub API integration, web scraping, data validation

```yaml
name: data-enhancer
capabilities:
  - github_api_integration
  - web_scraping
  - data_validation
  - package_manager_apis
tools:
  - web_fetch
  - execute_bash
  - fs_write
  - fs_read
context: |
  You are a data enhancement specialist focused on enriching DevOps tool information.
  Your primary responsibilities:
  - Fetch GitHub repository statistics
  - Scrape package manager data
  - Validate data quality and consistency
  - Update tool metadata automatically
```

### 2. AI Integration Subagent
**Purpose**: Handle AI-powered features and analysis
**Specialization**: Gemini API integration, natural language processing

```yaml
name: ai-processor
capabilities:
  - gemini_api_integration
  - natural_language_processing
  - tool_comparison_analysis
  - content_generation
tools:
  - web_search
  - fs_write
  - execute_bash
context: |
  You are an AI integration specialist focused on leveraging Google Gemini for intelligent features.
  Your primary responsibilities:
  - Generate AI-powered tool comparisons
  - Process natural language queries
  - Create intelligent tool descriptions
  - Analyze user preferences for recommendations
```

### 3. Frontend Development Subagent
**Purpose**: Handle React/TypeScript development tasks
**Specialization**: Component development, UI/UX implementation

```yaml
name: frontend-developer
capabilities:
  - react_component_development
  - typescript_implementation
  - ui_ux_design
  - responsive_design
tools:
  - fs_write
  - fs_read
  - execute_bash
  - glob
context: |
  You are a frontend development specialist focused on React/TypeScript implementation.
  Your primary responsibilities:
  - Create reusable React components
  - Implement TypeScript interfaces
  - Ensure responsive design
  - Optimize frontend performance
```

### 4. Backend API Subagent
**Purpose**: Handle FastAPI development and database operations
**Specialization**: API development, database management, authentication

```yaml
name: backend-developer
capabilities:
  - fastapi_development
  - database_management
  - authentication_systems
  - api_optimization
tools:
  - fs_write
  - fs_read
  - execute_bash
context: |
  You are a backend development specialist focused on FastAPI and database operations.
  Your primary responsibilities:
  - Develop REST API endpoints
  - Manage database schemas and migrations
  - Implement authentication systems
  - Optimize API performance
```

## Subagent Usage Patterns

### Pattern 1: Parallel Data Processing
```bash
# Delegate multiple data enhancement tasks simultaneously
use_subagent InvokeSubagents {
  "subagents": [
    {
      "agent_name": "data-enhancer",
      "query": "Update GitHub statistics for all tools in the database",
      "relevant_context": "Focus on star count, fork count, and last commit date"
    },
    {
      "agent_name": "ai-processor", 
      "query": "Generate AI descriptions for tools missing summaries",
      "relevant_context": "Use Gemini API to create technical summaries"
    }
  ]
}
```

### Pattern 2: Feature Development Workflow
```bash
# Coordinate frontend and backend development
use_subagent InvokeSubagents {
  "subagents": [
    {
      "agent_name": "frontend-developer",
      "query": "Create a new ToolComparison component with TypeScript interfaces",
      "relevant_context": "Component should accept tool IDs and display comparison matrix"
    },
    {
      "agent_name": "backend-developer",
      "query": "Implement /api/tools/compare endpoint with AI integration", 
      "relevant_context": "Endpoint should accept tool IDs and return comparison data"
    }
  ]
}
```

### Pattern 3: Quality Assurance Pipeline
```bash
# Parallel testing and validation
use_subagent InvokeSubagents {
  "subagents": [
    {
      "agent_name": "frontend-developer",
      "query": "Run TypeScript compilation and build tests",
      "relevant_context": "Check for type errors and build issues"
    },
    {
      "agent_name": "backend-developer", 
      "query": "Test all API endpoints and validate responses",
      "relevant_context": "Ensure all endpoints return proper status codes and data"
    },
    {
      "agent_name": "data-enhancer",
      "query": "Validate data quality and consistency across all tools",
      "relevant_context": "Check for missing fields and data anomalies"
    }
  ]
}
```

## Subagent Communication Protocols

### Task Delegation Guidelines
1. **Isolation**: Each subagent operates independently with isolated context
2. **Specialization**: Delegate tasks based on subagent expertise
3. **Parallel Processing**: Use multiple subagents for independent tasks
4. **Context Sharing**: Provide relevant context without overwhelming details

### Error Handling
- Subagents report errors independently
- Main agent coordinates retry logic
- Fallback mechanisms for critical operations
- Comprehensive logging for debugging

### Performance Optimization
- Parallel execution for independent tasks
- Context minimization to reduce overhead
- Task batching for related operations
- Resource monitoring and management

## Implementation Examples

### Example 1: Complete Feature Implementation
```bash
# Implement user authentication feature
use_subagent InvokeSubagents {
  "subagents": [
    {
      "agent_name": "backend-developer",
      "query": "Implement OAuth endpoints for Google and GitHub authentication",
      "relevant_context": "Use Authlib for OAuth implementation, store JWT tokens securely"
    },
    {
      "agent_name": "frontend-developer",
      "query": "Create authentication UI components with OAuth buttons",
      "relevant_context": "Design should match existing UI, include loading states"
    },
    {
      "agent_name": "data-enhancer",
      "query": "Set up user profile data enhancement from OAuth providers",
      "relevant_context": "Extract user information and preferences from OAuth responses"
    }
  ]
}
```

### Example 2: Performance Optimization
```bash
# Optimize application performance
use_subagent InvokeSubagents {
  "subagents": [
    {
      "agent_name": "frontend-developer",
      "query": "Implement code splitting and lazy loading for React components",
      "relevant_context": "Focus on reducing initial bundle size"
    },
    {
      "agent_name": "backend-developer",
      "query": "Add database indexing and query optimization",
      "relevant_context": "Optimize frequently used queries and add appropriate indexes"
    },
    {
      "agent_name": "ai-processor",
      "query": "Implement caching for AI-generated content",
      "relevant_context": "Cache comparison results and tool descriptions"
    }
  ]
}
```

### Example 3: Data Pipeline Enhancement
```bash
# Enhance data collection and processing
use_subagent InvokeSubagents {
  "subagents": [
    {
      "agent_name": "data-enhancer",
      "query": "Implement automated data collection from package managers",
      "relevant_context": "Collect download statistics from npm, PyPI, Docker Hub"
    },
    {
      "agent_name": "ai-processor",
      "query": "Generate tool categories and tags using AI analysis",
      "relevant_context": "Analyze tool descriptions to suggest appropriate categories"
    }
  ]
}
```

## Best Practices

### Subagent Selection
- Choose subagents based on task specialization
- Consider parallel processing opportunities
- Minimize context overlap between subagents
- Plan for error handling and recovery

### Task Decomposition
- Break complex features into independent subtasks
- Identify dependencies between tasks
- Prioritize critical path operations
- Plan for incremental delivery

### Context Management
- Provide sufficient context without overwhelming
- Include relevant technical constraints
- Specify expected outcomes clearly
- Document assumptions and requirements

### Quality Assurance
- Implement validation at each subagent level
- Coordinate integration testing
- Monitor subagent performance
- Maintain comprehensive logging

## Monitoring & Metrics

### Subagent Performance
- Task completion time per subagent
- Error rates and retry statistics
- Resource utilization monitoring
- Context efficiency metrics

### System Integration
- Cross-subagent communication patterns
- Task dependency resolution time
- Overall feature delivery velocity
- Quality metrics and defect rates

This subagent configuration enables CloudEngineered to leverage specialized AI agents for complex, parallel task execution while maintaining high quality and performance standards.
