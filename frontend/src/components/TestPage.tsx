import React, { useState, useEffect } from 'react';

const TestPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const testAPI = async () => {
      try {
        console.log('Testing API...');
        const response = await fetch('http://localhost:8000/api/blogs');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Data received:', result);
        setData(result);
      } catch (err) {
        console.error('API Error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    testAPI();
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Blog API Test</h1>
      
      {loading && <p>Loading...</p>}
      
      {error && (
        <div style={{ color: 'red', background: '#ffe6e6', padding: '10px', border: '1px solid red' }}>
          Error: {error}
        </div>
      )}
      
      {data && (
        <div>
          <h2>Success! Found {data.length} blogs:</h2>
          {data.slice(0, 3).map((blog: any) => (
            <div key={blog.id} style={{ border: '1px solid #ccc', margin: '10px 0', padding: '10px' }}>
              <h3>{blog.title}</h3>
              <p>By: {blog.author}</p>
              <p>Content length: {blog.content?.length || 0} chars</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TestPage;
