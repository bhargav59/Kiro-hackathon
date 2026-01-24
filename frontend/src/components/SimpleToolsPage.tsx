import React, { useState, useEffect } from 'react';

const SimpleToolsPage: React.FC = () => {
  const [tools, setTools] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchTools = async () => {
      try {
        console.log('Fetching tools...');
        const response = await fetch('http://localhost:8000/api/tools');
        console.log('Response status:', response.status);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        console.log('Tools received:', data.length);
        setTools(data);
      } catch (err) {
        console.error('Error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchTools();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>Loading Tools...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h1>Error: {error}</h1>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Hero Header */}
        <div style={{
          textAlign: 'center',
          color: 'white',
          marginBottom: '40px',
          padding: '40px 20px'
        }}>
          <h1 style={{
            fontSize: '3.5rem',
            fontWeight: 'bold',
            marginBottom: '20px',
            textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
          }}>
            🚀 DevOps Arsenal
          </h1>
          <p style={{
            fontSize: '1.2rem',
            opacity: 0.9,
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            {tools.length} Enterprise-Grade Tools for Modern Infrastructure
          </p>
        </div>

        {/* Tools Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '25px'
        }}>
          {tools.map((tool) => {
            const colors: Record<string, { bg: string; icon: string }> = {
              'Container': { bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: '🐳' },
              'Container Orchestration': { bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: '☸️' },
              'CI/CD': { bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: '🔄' },
              'Infrastructure as Code': { bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: '🏗️' },
              'Configuration Management': { bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', icon: '⚙️' },
              'Monitoring': { bg: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', icon: '📊' },
              'Observability': { bg: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', icon: '👁️' },
              'Logging': { bg: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)', icon: '📝' },
              'Service Mesh': { bg: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', icon: '🕸️' },
              'Service Discovery': { bg: 'linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)', icon: '🔍' },
              'Security': { bg: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)', icon: '🔒' },
              'GitOps': { bg: 'linear-gradient(135deg, #48cae4 0%, #023e8a 100%)', icon: '🔄' },
              'Package Management': { bg: 'linear-gradient(135deg, #96fbc4 0%, #f9f047 100%)', icon: '📦' },
              'Storage': { bg: 'linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%)', icon: '💾' },
              'API Gateway': { bg: 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)', icon: '🌐' },
              'Load Balancer': { bg: 'linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)', icon: '⚖️' },
              'Proxy': { bg: 'linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%)', icon: '🔀' }
            };

            const categoryStyle = colors[tool.category] || colors['Container'];

            return (
              <div key={tool.id}
                style={{
                  background: 'white',
                  borderRadius: '20px',
                  overflow: 'hidden',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  cursor: 'pointer'
                }}
                onClick={() => {
                  if (tool.homepage_url) {
                    window.open(tool.homepage_url, '_blank');
                  } else if (tool.github_url) {
                    window.open(tool.github_url, '_blank');
                  }
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px) scale(1.02)';
                  e.currentTarget.style.boxShadow = '0 30px 60px rgba(0,0,0,0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0) scale(1)';
                  e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
                }}>

                {/* Header with gradient */}
                <div style={{
                  background: categoryStyle.bg,
                  padding: '25px',
                  color: 'white',
                  position: 'relative'
                }}>
                  <div style={{
                    fontSize: '2.5rem',
                    position: 'absolute',
                    top: '15px',
                    right: '20px',
                    opacity: 0.7
                  }}>
                    {categoryStyle.icon}
                  </div>

                  {/* Click indicator */}
                  <div style={{
                    position: 'absolute',
                    top: '10px',
                    left: '20px',
                    background: 'rgba(255,255,255,0.2)',
                    padding: '4px 8px',
                    borderRadius: '12px',
                    fontSize: '0.7rem',
                    fontWeight: '600'
                  }}>
                    👆 Click to visit
                  </div>

                  <h3 style={{
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    marginBottom: '8px',
                    marginTop: '15px',
                    textShadow: '1px 1px 2px rgba(0,0,0,0.2)'
                  }}>
                    {tool.name}
                  </h3>

                  <div style={{
                    fontSize: '0.9rem',
                    opacity: 0.9,
                    marginBottom: '10px'
                  }}>
                    {tool.category}
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px'
                  }}>
                    <span style={{
                      background: 'rgba(255,255,255,0.2)',
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '0.8rem',
                      fontWeight: '600'
                    }}>
                      ⭐ {tool.github_stars?.toLocaleString()}
                    </span>

                    <span style={{
                      background: tool.pricing_model === 'free' ? '#00b894' :
                        tool.pricing_model === 'freemium' ? '#0984e3' : '#6c5ce7',
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '0.8rem',
                      fontWeight: '600',
                      textTransform: 'uppercase'
                    }}>
                      {tool.pricing_model}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div style={{ padding: '25px' }}>
                  <p style={{
                    color: '#666',
                    lineHeight: '1.6',
                    marginBottom: '20px',
                    fontSize: '0.95rem'
                  }}>
                    {tool.ai_summary || tool.description?.substring(0, 120)}...
                  </p>

                  <div style={{
                    display: 'flex',
                    gap: '10px',
                    flexWrap: 'wrap'
                  }}>
                    {tool.homepage_url && (
                      <a
                        href={tool.homepage_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          padding: '8px 16px',
                          borderRadius: '25px',
                          textDecoration: 'none',
                          fontSize: '0.85rem',
                          fontWeight: '600',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '5px',
                          transition: 'transform 0.2s ease'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                        onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                      >
                        🌐 Website
                      </a>
                    )}

                    {tool.github_url && (
                      <a
                        href={tool.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          background: 'linear-gradient(135deg, #333 0%, #555 100%)',
                          color: 'white',
                          padding: '8px 16px',
                          borderRadius: '25px',
                          textDecoration: 'none',
                          fontSize: '0.85rem',
                          fontWeight: '600',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '5px',
                          transition: 'transform 0.2s ease'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                        onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                      >
                        🔗 GitHub
                      </a>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Stats Footer */}
        <div style={{
          background: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          padding: '30px',
          marginTop: '40px',
          textAlign: 'center',
          color: 'white'
        }}>
          <h2 style={{ fontSize: '2rem', marginBottom: '20px' }}>🎯 Platform Statistics</h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px'
          }}>
            <div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#ffeaa7' }}>{tools.length}</div>
              <div>Total Tools</div>
            </div>
            <div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#81ecec' }}>
                {tools.reduce((sum, tool) => sum + (tool.github_stars || 0), 0).toLocaleString()}
              </div>
              <div>GitHub Stars</div>
            </div>
            <div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#fd79a8' }}>
                {tools.filter(tool => tool.pricing_model === 'free').length}
              </div>
              <div>Free Tools</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleToolsPage;
