import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../utils/axios';

function CommentsListScreen({ setComment }) {
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isMockData, setIsMockData] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLatestComments();
  }, []);

  const fetchLatestComments = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get('/api/v1/comments/latest');
      setComments(response.data.comments || []);
      setIsMockData(response.data.is_mock || false);
    } catch (err) {
      console.error('Error fetching comments:', err);
      setError(err.response?.data?.detail || 'Failed to fetch comments');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectComment = (comment) => {
    setComment(comment);
    navigate('/reply');
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now - date) / (1000 * 60));
      return `${diffInMinutes} minutes ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours} hours ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays} days ago`;
    }
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="loading">
          <div className="spinner"></div>
          <p style={{ marginLeft: '10px' }}>Fetching latest comments...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2>Error</h2>
        <p style={{ color: 'red' }}>{error}</p>
        <button className="btn" onClick={fetchLatestComments}>
          Try Again
        </button>
      </div>
    );
  }

  if (!comments || comments.length === 0) {
    return (
      <div className="card">
        <h2>No Comments Found</h2>
        <p>No comments found on your recent posts.</p>
        <button className="btn" onClick={fetchLatestComments}>
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <h2>Latest Comments on Your Posts</h2>
        {isMockData && (
          <div style={{
            background: '#fff3cd',
            border: '1px solid #ffeaa7',
            color: '#856404',
            padding: '10px',
            borderRadius: '4px',
            marginBottom: '20px',
            fontSize: '0.9rem'
          }}>
            ⚠️ Showing sample comments. Connect your Instagram account to see real comments.
          </div>
        )}
        
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '15px',
          marginTop: '20px'
        }}>
          {comments.map((comment, index) => (
            <div 
              key={comment.id}
              style={{
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                padding: '20px',
                background: '#ffffff',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                position: 'relative'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
              onClick={() => handleSelectComment(comment)}
            >
              {/* Post Caption Header */}
              <div style={{ 
                background: '#f8f9fa', 
                margin: '-20px -20px 15px -20px',
                padding: '12px 20px',
                borderRadius: '8px 8px 0 0',
                borderBottom: '1px solid #e0e0e0'
              }}>
                <p style={{ 
                  margin: 0, 
                  fontSize: '0.85rem',
                  color: '#666',
                  fontStyle: 'italic',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  On your post: "{comment.post_caption}"
                </p>
              </div>

              {/* Comment Content */}
              <div style={{ 
                display: 'flex', 
                alignItems: 'flex-start',
                marginBottom: '12px'
              }}>
                <img 
                  src={comment.profile_pic_url} 
                  alt={comment.username}
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    marginRight: '12px'
                  }}
                  onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/40';
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '8px'
                  }}>
                    <h4 style={{ margin: 0 }}>@{comment.username}</h4>
                    <span style={{ 
                      fontSize: '0.85rem', 
                      color: '#666' 
                    }}>
                      {formatTimestamp(comment.timestamp)}
                    </span>
                  </div>
                  
                  <p style={{ 
                    fontSize: '1rem',
                    lineHeight: '1.5',
                    margin: '0',
                    color: '#333'
                  }}>
                    {comment.text}
                  </p>
                </div>
              </div>

              {/* Reply Button */}
              <button 
                className="btn"
                style={{
                  padding: '8px 20px',
                  fontSize: '0.9rem',
                  marginTop: '10px',
                  width: '100%'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectComment(comment);
                }}
              >
                Generate AI Reply
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px', textAlign: 'center' }}>
        <button 
          className="btn" 
          onClick={fetchLatestComments}
          style={{ 
            background: 'transparent',
            color: 'var(--primary)',
            border: '1px solid var(--primary)'
          }}
        >
          Refresh Comments
        </button>
      </div>
    </div>
  );
}

export default CommentsListScreen; 