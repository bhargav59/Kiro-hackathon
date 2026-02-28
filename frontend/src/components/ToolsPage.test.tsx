import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import ToolsPage from './ToolsPage';

// Mock the fetch API
globalThis.fetch = vi.fn() as any;

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithClient = (ui: React.ReactElement) => {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('ToolsPage', () => {
  it('renders loading state initially', () => {
    // Mock fetch to return a pending promise
    (globalThis.fetch as any).mockImplementationOnce(() => new Promise(() => {}));
    
    renderWithClient(<ToolsPage />);
    
    expect(screen.getByText(/Loading DevOps tools.../i)).toBeInTheDocument();
  });

  it('renders error state when fetch fails', async () => {
    // Mock fetch to reject
    (globalThis.fetch as any).mockImplementationOnce(() => Promise.reject(new Error('Failed to fetch')));
    
    renderWithClient(<ToolsPage />);
    
    // Wait for error state
    const errorElement = await screen.findByText(/Error Loading Tools/i);
    expect(errorElement).toBeInTheDocument();
  });

  it('renders tools when fetch succeeds', async () => {
    const mockTools = [
      {
        id: 1,
        name: 'Docker',
        slug: 'docker',
        description: 'Containerization platform',
        category: 'Container',
        pricing_model: 'free',
        github_stars: 1000,
        github_forks: 100,
        created_at: '2023-01-01',
      }
    ];

    (globalThis.fetch as any).mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockTools),
      })
    );

    renderWithClient(<ToolsPage />);

    // Wait for the tool to be rendered
    const toolName = await screen.findByText('Docker');
    expect(toolName).toBeInTheDocument();
    expect(screen.getByText('Containerization platform')).toBeInTheDocument();
  });
});
