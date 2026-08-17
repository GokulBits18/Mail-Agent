import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer 
} from 'recharts';
import { RefreshCw, Send, Edit3, Inbox, ShieldAlert, Eye } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const PRIORITY_COLORS = {
  High: '#fc0000',
  Medium: '#ffff03',
  Low: '#00ff33',
  Spam: '#4B5563',
  Unassigned: '#6B7280'
};

const RAINBOW_COLORS = ['#FF4500', '#FFD700', '#1bff1b', '#41cfff', '#9370DB'];

export default function App() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);
  
  // NEW: Track whether we are 'reviewing' a draft or 'viewing' a sent message
  const [modalMode, setModalMode] = useState('review'); 
  
  const [editedReply, setEditedReply] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [viewTab, setViewTab] = useState('Inbox');

  const loadEmails = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/emails`);
      setEmails(res.data.data || []);
    } catch (err) {
      console.error('Failed to fetch emails:', err);
    }
  };

  useEffect(() => {
    loadEmails();
  }, []);

  const syncInbox = async () => {
    setLoading(true);
    try {
      await axios.get(`${API_BASE}/api/process-emails`);
      await loadEmails();
    } catch (err) {
      alert('Error fetching or processing emails.');
    } finally {
      setLoading(false);
    }
  };

  const handleReview = (email) => {
    setSelectedEmail(email);
    setModalMode('review');
    setEditedReply(email.draft_reply_1 || '');
  };

  // NEW: Function to handle viewing an already sent email
  const handleView = (email) => {
    setSelectedEmail(email);
    setModalMode('view');
  };

  const handleApprove = async () => {
    if (!selectedEmail) return;
    setActionLoading(true);
    try {
      await axios.post(`${API_BASE}/api/emails/${selectedEmail.id}/approve`, {
        final_reply: editedReply
      });
      setSelectedEmail(null);
      await loadEmails();
    } catch (err) {
      alert('Failed to send approved email.');
    } finally {
      setActionLoading(false);
    }
  };

  const priorityCounts = emails.reduce((acc, curr) => {
    const p = curr.priority || 'Unassigned';
    acc[p] = (acc[p] || 0) + 1;
    return acc;
  }, {});

  const pieData = Object.keys(priorityCounts).map((key) => ({
    name: key,
    value: priorityCounts[key]
  }));

  const senderCounts = emails.reduce((acc, curr) => {
    const s = curr.sender ? curr.sender.split('<')[0].trim() : 'Unknown';
    acc[s] = (acc[s] || 0) + 1;
    return acc;
  }, {});

  const barData = Object.keys(senderCounts).slice(0, 5).map((sender) => ({
    sender: sender.length > 15 ? `${sender.substring(0, 12)}...` : sender,
    count: senderCounts[sender]
  }));

  const displayedEmails = emails.filter((email) => {
    if (viewTab === 'Spam') return email.priority === 'Spam';
    return email.priority !== 'Spam';
  });

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif', backgroundColor: '#E0F7FA', minHeight: '100vh' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#0F172A', margin: 0 }}>
            AI Email Triage Dashboard
          </h1>
          <p style={{ color: '#475569', margin: '4px 0 0 0' }}>
            Automated priority classification & human-in-the-loop email workflow
          </p>
        </div>
        <button
          onClick={syncInbox}
          disabled={loading}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            backgroundColor: '#0891B2', color: '#FFF', border: 'none',
            padding: '10px 16px', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: '600', boxShadow: '0 4px 6px -1px rgba(8, 145, 178, 0.4)'
          }}
        >
          <RefreshCw size={18} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          {loading ? 'Processing Inbox...' : 'Sync & Process'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#FFF', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '16px', color: '#0F172A' }}>Priority Breakdown</h3>
          <div style={{ height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PRIORITY_COLORS[entry.name] || '#6B7280'} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={{ backgroundColor: '#FFF', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '16px', color: '#0F172A' }}>Top Senders</h3>
          <div style={{ height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="sender" stroke="#64748b" />
                <YAxis allowDecimals={false} stroke="#64748b" />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={RAINBOW_COLORS[index % RAINBOW_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
        <button
          onClick={() => setViewTab('Inbox')}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '8px 16px', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', border: 'none',
            backgroundColor: viewTab === 'Inbox' ? '#0284C7' : '#FFF',
            color: viewTab === 'Inbox' ? '#FFF' : '#475569', boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}
        >
          <Inbox size={16} /> Inbox
        </button>
        <button
          onClick={() => setViewTab('Spam')}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '8px 16px', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', border: 'none',
            backgroundColor: viewTab === 'Spam' ? '#4B5563' : '#FFF',
            color: viewTab === 'Spam' ? '#FFF' : '#475569', boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}
        >
          <ShieldAlert size={16} /> Spam
        </button>
      </div>

      <div style={{ backgroundColor: '#FFF', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead style={{ backgroundColor: '#F0F9FF', borderBottom: '2px solid #BAE6FD' }}>
            <tr>
              <th style={{ padding: '12px 16px', fontSize: '14px', color: '#0284C7', fontWeight: '600' }}>Sender</th>
              <th style={{ padding: '12px 16px', fontSize: '14px', color: '#0284C7', fontWeight: '600' }}>Subject</th>
              <th style={{ padding: '12px 16px', fontSize: '14px', color: '#0284C7', fontWeight: '600' }}>Priority</th>
              <th style={{ padding: '12px 16px', fontSize: '14px', color: '#0284C7', fontWeight: '600' }}>Sentiment</th>
              <th style={{ padding: '12px 16px', fontSize: '14px', color: '#0284C7', fontWeight: '600' }}>Status</th>
              <th style={{ padding: '12px 16px', fontSize: '14px', color: '#0284C7', fontWeight: '600' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {displayedEmails.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '32px', color: '#9CA3AF' }}>
                  No emails in this view.
                </td>
              </tr>
            ) : (
              displayedEmails.map((email) => (
                <tr key={email.id} style={{ borderBottom: '1px solid #E2E8F0' }}>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#0F172A' }}>{email.sender}</td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#334155' }}>{email.subject}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      backgroundColor: `${PRIORITY_COLORS[email.priority] || '#6B7280'}20`,
                      color: PRIORITY_COLORS[email.priority] || '#6B7280',
                      padding: '4px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold'
                    }}>
                      {email.priority}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      backgroundColor: '#F1F5F9', color: '#475569',
                      padding: '4px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: '600'
                    }}>
                      {email.sentiment || 'Neutral'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px' }}>
                    <span style={{
                      color: email.status === 'Approved & Sent' || email.status === 'Auto-Sent' ? '#059669' : '#0284C7',
                      fontWeight: '600'
                    }}>
                      {email.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    
                    {/* NEW: Conditional rendering for Actions */}
                    {email.status === 'Pending' && email.priority !== 'Spam' ? (
                      <button
                        onClick={() => handleReview(email)}
                        style={{
                          display: 'flex', alignItems: 'center', gap: '4px',
                          backgroundColor: '#0284C7', color: '#FFF', border: 'none',
                          padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '500'
                        }}
                      >
                        <Edit3 size={14} /> Review & Approve
                      </button>
                    ) : email.status === 'Auto-Sent' || email.status === 'Approved & Sent' ? (
                      <button
                        onClick={() => handleView(email)}
                        style={{
                          display: 'flex', alignItems: 'center', gap: '4px',
                          backgroundColor: '#F1F5F9', color: '#475569', border: '1px solid #CBD5E1',
                          padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600'
                        }}
                      >
                        <Eye size={14} /> View Reply
                      </button>
                    ) : (
                      <span style={{ color: '#94A3B8', fontSize: '13px' }}>Ignored</span>
                    )}

                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* NEW: The dynamic Modal */}
      {selectedEmail && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 50
        }}>
          <div style={{
            backgroundColor: '#FFF', borderRadius: '12px', width: '600px', maxWidth: '90%',
            padding: '24px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '12px', color: '#0F172A' }}>
              {modalMode === 'review' ? `Review Draft: ${selectedEmail.subject}` : `Thread: ${selectedEmail.subject}`}
            </h2>
            
            <div style={{ 
              marginBottom: '16px', padding: '12px', backgroundColor: '#F1F5F9', 
              borderRadius: '8px', fontSize: '13px', maxHeight: '150px', overflowY: 'auto' 
            }}>
              <strong style={{ color: '#334155' }}>Original Message:</strong>
              <p style={{ margin: '6px 0 0 0', color: '#475569', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {selectedEmail.content}
              </p>
            </div>

            {/* If we are VIEWING a sent message */}
            {modalMode === 'view' && (
              <div style={{ 
                marginBottom: '16px', padding: '12px', backgroundColor: '#ECFDF5', border: '1px solid #A7F3D0',
                borderRadius: '8px', fontSize: '13px', maxHeight: '150px', overflowY: 'auto' 
              }}>
                <strong style={{ color: '#065F46' }}>Sent Reply ({selectedEmail.status}):</strong>
                <p style={{ margin: '6px 0 0 0', color: '#064E3B', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {selectedEmail.final_reply || "No reply body recorded."}
                </p>
              </div>
            )}

            {/* If we are REVIEWING a pending message */}
            {modalMode === 'review' && (
              <>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px', color: '#0F172A' }}>
                  Select a Smart Reply:
                </label>
                
                <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                  <button
                    onClick={() => setEditedReply(selectedEmail.draft_reply_1)}
                    style={{ padding: '6px 12px', fontSize: '12px', borderRadius: '6px', backgroundColor: '#ECFDF5', color: '#065F46', border: '1px solid #A7F3D0', cursor: 'pointer', fontWeight: '600' }}
                  >
                     Positive / Accept
                  </button>
                  <button
                    onClick={() => setEditedReply(selectedEmail.draft_reply_2)}
                    style={{ padding: '6px 12px', fontSize: '12px', borderRadius: '6px', backgroundColor: '#FEF2F2', color: '#991B1B', border: '1px solid #FECACA', cursor: 'pointer', fontWeight: '600' }}
                  >
                     Polite Decline
                  </button>
                  <button
                    onClick={() => setEditedReply(selectedEmail.draft_reply_3)}
                    style={{ padding: '6px 12px', fontSize: '12px', borderRadius: '6px', backgroundColor: '#F0F9FF', color: '#0369A1', border: '1px solid #BAE6FD', cursor: 'pointer', fontWeight: '600' }}
                  >
                     Ask for Details
                  </button>
                </div>

                <textarea
                  rows="6"
                  value={editedReply}
                  onChange={(e) => setEditedReply(e.target.value)}
                  style={{
                    width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #CBD5E1',
                    fontFamily: 'inherit', fontSize: '14px', boxSizing: 'border-box', backgroundColor: '#F8FAFC'
                  }}
                />
              </>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
              <button
                onClick={() => setSelectedEmail(null)}
                style={{ padding: '8px 16px', border: '1px solid #CBD5E1', color: '#475569', backgroundColor: '#FFF', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}
              >
                {modalMode === 'view' ? 'Close' : 'Cancel'}
              </button>
              
              {modalMode === 'review' && (
                <button
                  onClick={handleApprove}
                  disabled={actionLoading}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '6px',
                    backgroundColor: '#0891B2', color: '#FFF', border: 'none',
                    padding: '8px 16px', borderRadius: '6px', cursor: actionLoading ? 'not-allowed' : 'pointer', fontWeight: '500'
                  }}
                >
                  <Send size={14} />
                  {actionLoading ? 'Sending...' : 'Approve & Send'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}