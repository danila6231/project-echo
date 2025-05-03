import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

function OutputScreen({ savedResult }) {
  const [result, setResult] = useState(savedResult);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { token } = useParams();
  
  useEffect(() => {
    // If we don't have a saved result, fetch it using the token
    if (!result && token) {
      fetchResult(token);
    }
  }, [result, token]);
  
  const fetchResult = async (token) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`/api/v1/result/${token}`);
      setResult(response.data);
    } catch (err) {
      console.error('Error fetching result:', err);
      setError(err.response?.data?.detail || 'Could not retrieve your results. The session may have expired.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p style={{ marginLeft: '10px' }}>Loading results...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="card">
        <h2>Error</h2>
        <p style={{ color: 'red' }}>{error}</p>
        <Link to="/" className="btn">Try Again</Link>
      </div>
    );
  }
  
  if (!result) {
    return null;
  }

  return (
    <div>
      <div className="card">
        <h2>Account Summary</h2>
        <p>{result.account_summary}</p>
      </div>
      
      <h2>Content Ideas</h2>
      {result.content_ideas.map((idea, index) => (
        <div key={index} className="card">
          <h3>{idea.title}</h3>
          
          <div style={{ marginTop: '15px' }}>
            <h4>Caption Draft</h4>
            <p style={{ whiteSpace: 'pre-line' }}>{idea.caption_draft}</p>
          </div>
          
          <div style={{ marginTop: '15px' }}>
            <h4>Hashtags</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
              {idea.hashtag_suggestions.map((tag, tagIndex) => (
                <span 
                  key={tagIndex}
                  style={{
                    background: 'var(--gray-light)',
                    padding: '4px 8px',
                    borderRadius: '16px',
                    fontSize: '0.9rem'
                  }}
                >
                  {tag.startsWith('#') ? tag : `#${tag}`}
                </span>
              ))}
            </div>
          </div>
          
          <div style={{ marginTop: '15px' }}>
            <h4>Post Theme</h4>
            <p>{idea.post_theme}</p>
          </div>
        </div>
      ))}
      
      <div style={{ textAlign: 'center', marginTop: '20px', marginBottom: '20px' }}>
        <p>
          <strong>Bookmark this page to access your ideas later</strong>
          <br />
          This result will be available for an hour.
        </p>
        
        <Link to="/" className="btn" style={{ marginTop: '10px' }}>
          Generate More Ideas
        </Link>
      </div>
    </div>
  );
}

export default OutputScreen; 