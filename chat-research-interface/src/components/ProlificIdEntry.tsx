import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import '../styles/ProlificIdEntry.css';

interface ProlificIdEntryProps {
  onProlificIdSet: (id: string) => void;
}

const ProlificIdEntry: React.FC<ProlificIdEntryProps> = ({ onProlificIdSet }) => {
  const [prolificId, setProlificId] = useState('');
  const [error, setError] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // Check if Prolific ID is already in URL parameters or localStorage
    const urlProlificId = searchParams.get('PROLIFIC_PID');
    const storedProlificId = localStorage.getItem('prolific_id');
    
    // FOR TESTING: Comment out the next section to always show entry form
    if (urlProlificId) {
      // If in URL, validate and store
      if (validateProlificId(urlProlificId)) {
        localStorage.setItem('prolific_id', urlProlificId);
        onProlificIdSet(urlProlificId);
        return;
      }
    }
    
    if (storedProlificId && validateProlificId(storedProlificId)) {
      // If stored and valid, use it
      onProlificIdSet(storedProlificId);
      return;
    }
  }, [searchParams, onProlificIdSet]);

  const validateProlificId = (id: string): boolean => {
    // Prolific IDs are typically 24 characters long and alphanumeric
    // Format: Usually starts with letters followed by numbers
    const prolificPattern = /^[A-Za-z0-9]{10,30}$/;
    return prolificPattern.test(id.trim());
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsValidating(true);

    const trimmedId = prolificId.trim();

    if (!trimmedId) {
      setError('Please enter your Prolific ID');
      setIsValidating(false);
      return;
    }

    if (!validateProlificId(trimmedId)) {
      setError('Please enter a valid Prolific ID (10-30 alphanumeric characters)');
      setIsValidating(false);
      return;
    }

    // Store in localStorage for persistence across pages
    localStorage.setItem('prolific_id', trimmedId);
    
    // Call the callback to update parent component
    onProlificIdSet(trimmedId);
    
    setIsValidating(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProlificId(e.target.value);
    if (error) {
      setError(''); // Clear error when user starts typing
    }
  };

  return (
    <div className="prolific-entry-container">
      <div className="prolific-entry-card">
        <div className="header">
          <h1 className="study-title">Interactive AI Research Study</h1>
          <p className="study-subtitle">University Research - Participant Verification</p>
        </div>

        <div className="entry-form">
          <h2>Enter Your Prolific ID</h2>
          <p className="instruction-text">
            To participate in this study, please enter your Prolific participant ID. 
            This ensures your responses are properly linked to your participation.
          </p>

          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label htmlFor="prolific-id" className="input-label">
                Prolific ID
              </label>
              <input
                id="prolific-id"
                type="text"
                value={prolificId}
                onChange={handleInputChange}
                placeholder="Enter your Prolific ID (e.g., 5f8c2a1b3d4e5f6g7h8i9j0k)"
                className={`id-input ${error ? 'error' : ''}`}
                maxLength={30}
                autoFocus
                disabled={isValidating}
              />
              {error && <div className="error-message">{error}</div>}
            </div>

            <button
              type="submit"
              className="continue-button"
              disabled={isValidating || !prolificId.trim()}
            >
              {isValidating ? 'Validating...' : 'Continue to Study'}
            </button>
          </form>

          <div className="help-info">
            <h3>Where do I find my Prolific ID?</h3>
            <ul>
              <li>Your Prolific ID is provided in the study invitation</li>
              <li>It's also available in your Prolific dashboard</li>
              <li>It typically contains both letters and numbers</li>
              <li>If you can't find it, please return to Prolific to get the correct link</li>
            </ul>
            
            <div className="privacy-note">
              <strong>Privacy Note:</strong> Your Prolific ID is used solely for linking your 
              responses and ensuring proper compensation. No other personal information is collected.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProlificIdEntry;