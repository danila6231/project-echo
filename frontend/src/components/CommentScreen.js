import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../utils/axios';

function CommentScreen({ setComment }) {
  const [latestComment, setLatestComment] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchLatestComment();
  }, []);

  const fetchLatestComment = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get('/api/v1/comments/latest-single');
      setLatestComment(response.data.comment);
      setComment(response.data.comment);
    } catch (err) {
      console.error('Error fetching comment:', err);
      setError(err.response?.data?.detail || 'Failed to fetch latest comment');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReply = () => {
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
          <p style={{ marginLeft: '10px' }}>Fetching latest comment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2>Error</h2>
        <p style={{ color: 'red' }}>{error}</p>
        <button className="btn" onClick={fetchLatestComment}>
          Try Again
        </button>
      </div>
    );
  }

  if (!latestComment) {
    return (
      <div className="card">
        <h2>No Comments Found</h2>
        <p>No comments found on your recent posts.</p>
        <button className="btn" onClick={fetchLatestComment}>
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <h2>Latest Comment on Your Post</h2>
        
        <div style={{ 
          background: '#f5f5f5', 
          padding: '15px', 
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <h4 style={{ margin: '0 0 10px 0' }}>Your Post:</h4>
          <p style={{ margin: 0, fontStyle: 'italic' }}>
            "{latestComment.post_caption}"
          </p>
        </div>

        <div style={{
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          padding: '20px',
          background: '#ffffff'
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center',
            marginBottom: '15px'
          }}>
            <img 
              src={latestComment.profile_pic_url} 
              alt={latestComment.username}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                marginRight: '12px'
              }}
            />
            <div>
              <h4 style={{ margin: 0 }}>@{latestComment.username}</h4>
              <p style={{ 
                margin: 0, 
                fontSize: '0.9rem', 
                color: '#666' 
              }}>
                {formatTimestamp(latestComment.timestamp)}
              </p>
            </div>
          </div>
          
          <p style={{ 
            fontSize: '1.1rem',
            lineHeight: '1.6',
            margin: '0'
          }}>
            {latestComment.text}
          </p>
        </div>

        <div style={{ marginTop: '25px', textAlign: 'center' }}>
          <button 
            className="btn" 
            onClick={handleGenerateReply}
            style={{ fontSize: '1.1rem', padding: '12px 30px' }}
          >
            Generate AI Reply
          </button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px', textAlign: 'center' }}>
        <p style={{ margin: '0 0 15px 0' }}>
          Want to see a different comment?
        </p>
        <button 
          className="btn" 
          onClick={fetchLatestComment}
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

export default CommentScreen; 