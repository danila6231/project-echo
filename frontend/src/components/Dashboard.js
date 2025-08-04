import React, { useState, useEffect } from 'react';
import axios from '../utils/axios';

function Dashboard() {
  const [comments, setComments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isLoadingComments, setIsLoadingComments] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(true);
  const [error, setError] = useState('');
  const [expandedItems, setExpandedItems] = useState({});
  const [loadingReplies, setLoadingReplies] = useState({});
  const [suggestedReplies, setSuggestedReplies] = useState({});
  const [editingReply, setEditingReply] = useState({});
  const [copiedIndex, setCopiedIndex] = useState(null);

  useEffect(() => {
    fetchLatestComments();
    fetchLatestMessages();
  }, []);

  const fetchLatestComments = async () => {
    setIsLoadingComments(true);
    setError('');
    
    try {
      const response = await axios.get('/api/v1/comments/latest');
      setComments(response.data.comments || []);
    } catch (err) {
      console.error('Error fetching comments:', err);
      setError(err.response?.data?.detail || 'Failed to fetch comments');
    } finally {
      setIsLoadingComments(false);
    }
  };

  const fetchLatestMessages = async () => {
    setIsLoadingMessages(true);
    setError('');
    
    try {
      const response = await axios.get('/api/v1/message/latest');
      setMessages(response.data.messages || []);
    } catch (err) {
      console.error('Error fetching messages:', err);
      setError(err.response?.data?.detail || 'Failed to fetch messages');
    } finally {
      setIsLoadingMessages(false);
    }
  };



  const toggleReplySuggestions = async (itemId, type) => {
    const key = `${type}-${itemId}`;
    
    if (expandedItems[key]) {
      // Collapse
      setExpandedItems(prev => ({ ...prev, [key]: false }));
    } else {
      // Expand and fetch suggestions if not already loaded
      setExpandedItems(prev => ({ ...prev, [key]: true }));
      
      if (!suggestedReplies[key]) {
        setLoadingReplies(prev => ({ ...prev, [key]: true }));
        
        try {
          const formData = new FormData();
          formData.append(`${type === 'comment' ? 'comment_id' : 'message_id'}`, itemId);
          
          if (type === 'comment') {
            const comment = comments.find(([c]) => c.id === itemId);
            if (comment) {
              formData.append('post_id', comment[0].post_id);
            }
          }
          
          const endpoint = type === 'comment' 
            ? '/api/v1/comments/suggest-reply' 
            : '/api/v1/messages/suggest-reply';
          
          const response = await axios.post(endpoint, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          
          setSuggestedReplies(prev => ({ ...prev, [key]: response.data }));
        } catch (err) {
          console.error('Error generating reply:', err);
          setError(err.response?.data?.detail || 'Failed to generate reply suggestion');
        } finally {
          setLoadingReplies(prev => ({ ...prev, [key]: false }));
        }
      }
    }
  };

  const handleEditReply = (key, replyIndex, newText) => {
    setEditingReply(prev => ({ ...prev, [`${key}-${replyIndex}`]: newText }));
  };

  const getEditedReplyText = (key, replyIndex, originalText) => {
    const editKey = `${key}-${replyIndex}`;
    return editingReply[editKey] !== undefined ? editingReply[editKey] : originalText;
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

  const getCombinedAndSortedItems = () => {
    const commentItems = comments.map(comment => ({
      data: comment,
      type: 'comment',
      sortDate: new Date(comment[0].timestamp)
    }));
    
    const messageItems = messages.map(message => ({
      data: message,
      type: 'message', 
      sortDate: new Date(message[0].created_time)
    }));
    
    return [...commentItems, ...messageItems].sort((a, b) => b.sortDate - a.sortDate);
  };

  const renderItem = (item) => {
    if (item.type === 'comment') {
      const [commentData, isNew] = item.data;
      const key = `comment-${commentData.id}`;
      const isExpanded = expandedItems[key];
      const isLoadingReply = loadingReplies[key];
      const replies = suggestedReplies[key];

      return (
        <div key={commentData.id} className={`interaction-item ${isNew ? 'new-comment' : ''}`}>
          <div className="interaction-header">
            <span className="item-type-label comment-label">Comment</span>
            <img 
              src={commentData.profile_pic_url} 
              alt={commentData.username}
              className="profile-pic"
              onError={(e) => { e.target.src = 'https://via.placeholder.com/40'; }}
            />
            <div className="interaction-info">
              <h4>@{commentData.username}</h4>
              <span className="timestamp">{formatTimestamp(commentData.timestamp)}</span>
            </div>
          </div>
          
          <div className="interaction-content">
            <p className="post-context">On your post: "{commentData.post_caption}"</p>
            <p className="interaction-text">{commentData.text}</p>
          </div>

          <div className="interaction-actions">
            <button 
              className="btn-secondary"
              onClick={() => toggleReplySuggestions(commentData.id, 'comment')}
            >
              {isExpanded ? '▼ Hide' : '▶ Show'} Reply Suggestions
            </button>
          </div>

          {isExpanded && (
            <div className="reply-suggestions">
              {isLoadingReply ? (
                <div className="loading">
                  <div className="spinner"></div>
                  <p>Generating AI replies...</p>
                </div>
              ) : replies ? (
                <>
                  <div className="suggested-reply primary">
                    <h5>Suggested Reply:</h5>
                    <textarea
                      className="reply-textarea"
                      value={getEditedReplyText(key, 'main', replies.suggested_reply.text)}
                      onChange={(e) => handleEditReply(key, 'main', e.target.value)}
                    />
                    <button
                      className="btn-copy"
                      onClick={() => copyToClipboard(getEditedReplyText(key, 'main', replies.suggested_reply.text), `${key}-main`)}
                    >
                      {copiedIndex === `${key}-main` ? '✓ Copied!' : 'Copy'}
                    </button>
                  </div>

                  {replies.alternative_replies && replies.alternative_replies.length > 0 && (
                    <div className="alternative-replies">
                      <h5>Alternative Replies:</h5>
                      {replies.alternative_replies.map((reply, index) => (
                        <div key={index} className="suggested-reply">
                          <textarea
                            className="reply-textarea"
                            value={getEditedReplyText(key, index, reply.text)}
                            onChange={(e) => handleEditReply(key, index, e.target.value)}
                          />
                          <button
                            className="btn-copy"
                            onClick={() => copyToClipboard(getEditedReplyText(key, index, reply.text), `${key}-${index}`)}
                          >
                            {copiedIndex === `${key}-${index}` ? '✓ Copied!' : 'Copy'}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : null}
            </div>
          )}
        </div>
      );
    } else {
      const [messageData, isNew] = item.data;
      const key = `message-${messageData.id}`;
      const isExpanded = expandedItems[key];
      const isLoadingReply = loadingReplies[key];
      const replies = suggestedReplies[key];
      const fromUsername = messageData.from?.username || 'Unknown';

      return (
        <div key={messageData.id} className={`interaction-item ${isNew ? 'new-comment' : ''}`}>
          <div className="interaction-header">
            <span className="item-type-label message-label">Direct Message</span>
            <div className="interaction-info">
              <h4>@{fromUsername}</h4>
              <span className="timestamp">{formatTimestamp(messageData.created_time)}</span>
            </div>
          </div>
          
          <div className="interaction-content">
            <p className="interaction-text">{messageData.message}</p>
          </div>

          <div className="interaction-actions">
            <button 
              className="btn-secondary"
              onClick={() => toggleReplySuggestions(messageData.id, 'message')}
            >
              {isExpanded ? '▼ Hide' : '▶ Show'} Reply Suggestions
            </button>
          </div>

          {isExpanded && (
            <div className="reply-suggestions">
              {isLoadingReply ? (
                <div className="loading">
                  <div className="spinner"></div>
                  <p>Generating AI replies...</p>
                </div>
              ) : replies ? (
                <>
                  <div className="suggested-reply primary">
                    <h5>Suggested Reply:</h5>
                    <textarea
                      className="reply-textarea"
                      value={getEditedReplyText(key, 'main', replies.suggested_reply.text)}
                      onChange={(e) => handleEditReply(key, 'main', e.target.value)}
                    />
                    <button
                      className="btn-copy"
                      onClick={() => copyToClipboard(getEditedReplyText(key, 'main', replies.suggested_reply.text), `${key}-main`)}
                    >
                      {copiedIndex === `${key}-main` ? '✓ Copied!' : 'Copy'}
                    </button>
                  </div>

                  {replies.alternative_replies && replies.alternative_replies.length > 0 && (
                    <div className="alternative-replies">
                      <h5>Alternative Replies:</h5>
                      {replies.alternative_replies.map((reply, index) => (
                        <div key={index} className="suggested-reply">
                          <textarea
                            className="reply-textarea"
                            value={getEditedReplyText(key, index, reply.text)}
                            onChange={(e) => handleEditReply(key, index, e.target.value)}
                          />
                          <button
                            className="btn-copy"
                            onClick={() => copyToClipboard(getEditedReplyText(key, index, reply.text), `${key}-${index}`)}
                          >
                            {copiedIndex === `${key}-${index}` ? '✓ Copied!' : 'Copy'}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : null}
            </div>
          )}
        </div>
      );
    }
  };

  const refreshAll = () => {
    fetchLatestComments();
    fetchLatestMessages();
  };

  const combinedItems = getCombinedAndSortedItems();
  const isLoading = isLoadingComments || isLoadingMessages;

  return (
    <div className="dashboard">
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      <div className="refresh-section">
        <button className="btn-outline" onClick={refreshAll}>
          Refresh All
        </button>
      </div>

      <div className="content-section">
        {isLoading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading...</p>
          </div>
        ) : combinedItems.length === 0 ? (
          <div className="empty-state">
            <p>No comments or messages found.</p>
            <button className="btn" onClick={refreshAll}>
              Refresh All
            </button>
          </div>
        ) : (
          <>
            {combinedItems.map(item => renderItem(item))}
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard; 