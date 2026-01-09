# Sourcery GitHub Integration Setup

## 1. Get Sourcery Token
1. Go to https://sourcery.ai/
2. Sign up/login with your GitHub account
3. Navigate to Settings → Tokens
4. Generate a new token for your repository

## 2. Add GitHub Secret
1. Go to your GitHub repository: https://github.com/bhargav59/Kiro-hackathon
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `SOURCERY_TOKEN`
5. Value: [paste your Sourcery token]

## 3. Enable Sourcery Bot (Optional)
1. Install Sourcery GitHub App: https://github.com/apps/sourcery-ai
2. Grant access to your repository
3. Sourcery will automatically review PRs and suggest improvements

## 4. Configuration Files Created
- `.github/workflows/sourcery.yml` - GitHub Actions workflow
- `.sourcery.yaml` - Sourcery configuration

## 5. Features Enabled
- ✅ Automatic code review on PRs
- ✅ Code quality checks on push to main
- ✅ Inline suggestions for improvements
- ✅ Python-specific optimizations
- ✅ Complexity analysis

## Next Steps
1. Add the SOURCERY_TOKEN secret
2. Push these changes to trigger the workflow
3. Create a test PR to see Sourcery in action
