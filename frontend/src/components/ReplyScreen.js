import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from '../utils/axios';

function ReplyScreen({ comment }) {
  const [replyData, setReplyData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [copiedIndex, setCopiedIndex] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!comment) {
      navigate('/');
      return;
    }
    generateReply();
  }, [comment, navigate]);

  const generateReply = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('comment_id', comment.id);
      
      const response = await axios.post('/api/v1/comments/suggest-reply', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setReplyData(response.data);
    } catch (err) {
      console.error('Error generating reply:', err);
      setError(err.response?.data?.detail || 'Failed to generate reply suggestion');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="loading">
          <div className="spinner"></div>
          <p style={{ marginLeft: '10px' }}>Analyzing account and generating reply...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2>Error</h2>
        <p style={{ color: 'red' }}>{error}</p>
        <Link to="/" className="btn">Back to Comments</Link>
      </div>
    );
  }

  if (!replyData) {
    return null;
  }

  return (
    <div>
      {/* Original Comment Reference */}
      <div className="card" style={{ background: '#f9f9f9' }}>
        <h3 style={{ margin: '0 0 10px 0' }}>Replying to:</h3>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <img 
            src={comment.profile_pic_url} 
            alt={comment.username}
            style={{
              width: '30px',
              height: '30px',
              borderRadius: '50%',
              marginRight: '10px'
            }}
          />
          <span style={{ fontWeight: 'bold' }}>@{comment.username}:</span>
          <span style={{ marginLeft: '10px' }}>{comment.text}</span>
        </div>
      </div>

      {/* Main Suggested Reply */}
      <div className="card">
        <h2>Suggested Reply</h2>
        
        <div style={{
          background: '#e3f2fd',
          border: '2px solid #1976d2',
          borderRadius: '8px',
          padding: '20px',
          position: 'relative'
        }}>
          <p style={{
            fontSize: '1.1rem',
            lineHeight: '1.6',
            margin: '0 0 15px 0'
          }}>
            {replyData.suggested_reply.text}
          </p>
          
          <button
            className="btn"
            onClick={() => copyToClipboard(replyData.suggested_reply.text, 'main')}
            style={{
              background: copiedIndex === 'main' ? '#4caf50' : 'var(--primary)',
              transition: 'background 0.3s'
            }}
          >
            {copiedIndex === 'main' ? 'Copied!' : 'Copy Reply'}
          </button>
        </div>

        {/* Reply Analysis */}
        <div style={{ marginTop: '20px' }}>
          <h4>Reply Analysis:</h4>
          <div style={{
            background: '#f5f5f5',
            padding: '15px',
            borderRadius: '8px'
          }}>
            <p><strong>Tone:</strong> {replyData.suggested_reply.tone}</p>
            <p><strong>Account Type:</strong> {replyData.suggested_reply.analysis.account_type}</p>
            <p><strong>Strategy:</strong> {replyData.suggested_reply.analysis.engagement_strategy}</p>
            <p><strong>Personalization:</strong> {replyData.suggested_reply.analysis.personalization}</p>
            {replyData.suggested_reply.includes_cta && (
              <p style={{ color: '#4caf50' }}><strong>✓ Includes Call-to-Action</strong></p>
            )}
          </div>
        </div>
      </div>

      {/* Alternative Replies */}
      <div className="card">
        <h3>Alternative Reply Options</h3>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Choose a different tone or approach:
        </p>
        
        {replyData.alternative_replies.map((reply, index) => (
          <div
            key={index}
            style={{
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              padding: '15px',
              marginBottom: '15px',
              background: '#ffffff'
            }}
          >
            <p style={{
              fontSize: '1rem',
              lineHeight: '1.5',
              margin: '0 0 10px 0'
            }}>
              {reply.text}
            </p>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span style={{
                fontSize: '0.9rem',
                color: '#666',
                fontStyle: 'italic'
              }}>
                Tone: {reply.tone}
              </span>
              <button
                className="btn"
                onClick={() => copyToClipboard(reply.text, index)}
                style={{
                  padding: '5px 15px',
                  fontSize: '0.9rem',
                  background: copiedIndex === index ? '#4caf50' : 'transparent',
                  color: copiedIndex === index ? 'white' : 'var(--primary)',
                  border: `1px solid ${copiedIndex === index ? '#4caf50' : 'var(--primary)'}`,
                  transition: 'all 0.3s'
                }}
              >
                {copiedIndex === index ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div style={{ textAlign: 'center', marginTop: '30px', marginBottom: '30px' }}>
        <Link to="/" className="btn" style={{ marginRight: '15px' }}>
          Analyze Another Comment
        </Link>
        <button 
          className="btn" 
          onClick={generateReply}
          style={{
            background: 'transparent',
            color: 'var(--primary)',
            border: '1px solid var(--primary)'
          }}
        >
          Regenerate Suggestions
        </button>
      </div>
    </div>
  );
}

export default ReplyScreen; 