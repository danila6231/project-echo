import React, { useState, useEffect } from 'react';
import axios from '../utils/axios';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('comments');
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
    // Set messages loading to false after initial load since we lazy load messages
    setIsLoadingMessages(false);
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

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'messages' && messages.length === 0 && !isLoadingMessages) {
      fetchLatestMessages();
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

  const renderCommentItem = (comment) => {
    const [commentData, isNew] = comment;
    const key = `comment-${commentData.id}`;
    const isExpanded = expandedItems[key];
    const isLoadingReply = loadingReplies[key];
    const replies = suggestedReplies[key];

    return (
      <div key={commentData.id} className={`interaction-item ${isNew ? 'new-comment' : ''}`}>
        <div className="interaction-header">
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
  };

  const renderMessageItem = (message) => {
    const [messageData, isNew] = message;
    const key = `message-${messageData.id}`;
    const isExpanded = expandedItems[key];
    const isLoadingReply = loadingReplies[key];
    const replies = suggestedReplies[key];
    const fromUsername = messageData.from?.username || 'Unknown';
    // console.log(messageData);

    return (
      <div key={messageData.id} className={`interaction-item ${isNew ? 'new-comment' : ''}`}>
        <div className="interaction-header">
          {/* <img 
            src={'https://via.placeholder.com/40'} 
            alt={fromUsername}
            className="profile-pic"
            onError={(e) => { e.target.src = 'https://via.placeholder.com/40'; }}
          /> */}
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
  };

  return (
    <div className="dashboard">
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'comments' ? 'active' : ''}`}
          onClick={() => handleTabChange('comments')}
        >
          Latest Comments
        </button>
        <button 
          className={`tab ${activeTab === 'messages' ? 'active' : ''}`}
          onClick={() => handleTabChange('messages')}
        >
          Latest Messages
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      <div className="tab-content">
        {activeTab === 'comments' ? (
          <div className="comments-section">
            {isLoadingComments ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>Loading comments...</p>
              </div>
            ) : comments.length === 0 ? (
              <div className="empty-state">
                <p>No comments found on your recent posts.</p>
                <button className="btn" onClick={fetchLatestComments}>
                  Refresh Comments
                </button>
              </div>
            ) : (
              <>
                {comments.map(comment => renderCommentItem(comment))}
                <div className="refresh-section">
                  <button className="btn-outline" onClick={fetchLatestComments}>
                    Refresh Comments
                  </button>
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="messages-section">
            {isLoadingMessages ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>Loading messages...</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="empty-state">
                <p>No messages found in your Instagram Direct.</p>
                <button className="btn" onClick={fetchLatestMessages}>
                  Refresh Messages
                </button>
              </div>
            ) : (
              <>
                {messages.map(message => renderMessageItem(message))}
                <div className="refresh-section">
                  <button className="btn-outline" onClick={fetchLatestMessages}>
                    Refresh Messages
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard; 