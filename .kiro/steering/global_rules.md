# CloudEngineered - Global Rules & Standards

## Architecture Principles

### 1. AI-First Design
- All features should leverage AI capabilities where possible
- Fallback systems required for AI service unavailability
- Progressive enhancement with AI features

### 2. Component-Driven Development
- Reusable React components with TypeScript
- Single responsibility principle
- Props interface definitions required

### 3. API-First Architecture
- RESTful endpoints with OpenAPI documentation
- Consistent error handling and response formats
- Input validation with Pydantic models

### 4. Security by Design
- OAuth-first authentication strategy
- JWT token management
- Input sanitization and validation
- CORS configuration

## Coding Standards

### Backend (Python/FastAPI)
```python
# File naming: snake_case
# Class naming: PascalCase
# Function naming: snake_case
# Constants: UPPER_SNAKE_CASE

# Required imports order:
# 1. Standard library
# 2. Third-party packages
# 3. Local imports

# Error handling pattern:
try:
    result = operation()
    return {"success": True, "data": result}
except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### Frontend (TypeScript/React)
```typescript
// File naming: PascalCase for components, camelCase for utilities
// Interface naming: PascalCase with 'I' prefix optional
// Component props: ComponentNameProps

// Required component structure:
interface ComponentProps {
  // Props definition
}

const Component: React.FC<ComponentProps> = ({ prop }) => {
  // Component logic
  return (
    // JSX with proper className usage
  );
};

export default Component;
```

### Database Design
- Use SQLAlchemy ORM models
- Proper relationships with back_populates
- Index frequently queried fields
- Use UTC timestamps
- Soft deletes where applicable

## Technical Approach

### 1. Development Workflow
- Feature branch development
- Comprehensive testing before merge
- Documentation updates with code changes
- Performance considerations for all features

### 2. Data Management
- Multi-source data enhancement pipeline
- Real-time updates where possible
- Caching strategy for expensive operations
- Data validation at all entry points

### 3. User Experience
- Mobile-first responsive design
- Accessibility compliance (WCAG 2.1 AA)
- Progressive loading and error states
- Clear user feedback for all actions

### 4. Performance Standards
- API response times < 200ms for cached data
- Page load times < 2 seconds
- Lazy loading for non-critical components
- Optimized database queries

## Quality Gates

### Code Quality
- TypeScript strict mode enabled
- ESLint and Prettier configuration
- Python type hints where applicable
- Comprehensive error handling

### Testing Requirements
- API endpoint testing with curl
- Component rendering validation
- Database operation verification
- OAuth flow testing

### Documentation Standards
- Inline code comments for complex logic
- API documentation with examples
- Component prop documentation
- Architecture decision records
