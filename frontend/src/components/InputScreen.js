import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from '../utils/axios';

function InputScreen({ setResult }) {
  const [files, setFiles] = useState([]);
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const onDrop = useCallback(acceptedFiles => {
    // Limit to 3 files
    const selectedFiles = acceptedFiles.slice(0, 3);
    setFiles(selectedFiles);
  }, []);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': []
    },
    maxFiles: 3,
    maxSize: 10485760 // 10MB max size
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please upload at least one screenshot');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    if (description) {
      formData.append('account_description', description);
    }
    
    try {
      const response = await axios.post('/api/v1/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Store the result in state
      setResult(response.data);
      
      // Navigate to results page with the token
      navigate(`/results/${response.data.token}`);
      
    } catch (err) {
      console.error('Error submitting form:', err);
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const removeFile = (index) => {
    setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
  };

  return (
    <div className="card">
      <h2>Generate Social Media Content Ideas</h2>
      <p>Upload screenshots of your social media profile to get personalized content suggestions.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Upload Screenshots (1-3 images)</label>
          <div 
            {...getRootProps()} 
            className="dropzone" 
            style={{
              border: '2px dashed #ccc',
              borderRadius: '4px',
              padding: '20px',
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? '#f0f8ff' : '#fafafa'
            }}
          >
            <input {...getInputProps()} />
            {
              isDragActive ?
                <p>Drop the files here...</p> :
                <p>Drag and drop screenshots here, or click to select files</p>
            }
          </div>
          
          {files.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <h4>Selected Files:</h4>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {files.map((file, index) => (
                  <li key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                    <img 
                      src={URL.createObjectURL(file)} 
                      alt={`Preview ${index}`} 
                      style={{ width: '60px', height: '60px', objectFit: 'cover', marginRight: '10px' }}
                    />
                    <span>{file.name}</span>
                    <button 
                      type="button" 
                      onClick={() => removeFile(index)}
                      style={{ marginLeft: '10px', background: 'none', border: 'none', color: 'red', cursor: 'pointer' }}
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Account Description (Optional)</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your account's niche, target audience, goals, and tone (e.g., 'Vegan food blog targeting young professionals')"
          />
        </div>
        
        {error && (
          <div style={{ color: 'red', marginBottom: '15px' }}>
            {error}
          </div>
        )}
        
        <button 
          type="submit" 
          className="btn" 
          disabled={isLoading}
        >
          {isLoading ? 'Generating Ideas...' : 'Generate Content Ideas'}
        </button>
      </form>
      
      {isLoading && (
        <div className="loading">
          <div className="spinner"></div>
          <p style={{ marginLeft: '10px' }}>Analyzing your content...</p>
        </div>
      )}
    </div>
  );
}

export default InputScreen; 