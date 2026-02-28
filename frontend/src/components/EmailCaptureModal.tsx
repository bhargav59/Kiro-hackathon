import React, { useState, useEffect } from 'react';
import { X, Mail } from 'lucide-react';
import { API_BASE } from '../config';
import { trackEvent } from '../analytics';

const EmailCaptureModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  useEffect(() => {
    const dismissed = localStorage.getItem('email_capture_dismissed');
    const subscribed = localStorage.getItem('email_subscribed');
    if (dismissed || subscribed) return;

    const visits = parseInt(localStorage.getItem('visit_count') || '0', 10) + 1;
    localStorage.setItem('visit_count', String(visits));

    // Show on 2nd visit
    if (visits >= 2) {
      const timer = setTimeout(() => setIsOpen(true), 5000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleDismiss = () => {
    setIsOpen(false);
    localStorage.setItem('email_capture_dismissed', 'true');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus('loading');
    try {
      const res = await fetch(`${API_BASE}/api/newsletter/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: 'modal' }),
      });
      if (res.ok) {
        setStatus('success');
        localStorage.setItem('email_subscribed', 'true');
        trackEvent('newsletter_subscribed', { source: 'modal' });
        setTimeout(() => setIsOpen(false), 2000);
      } else {
        setStatus('error');
      }
    } catch {
      setStatus('error');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 relative">
        <button onClick={handleDismiss} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X size={20} />
        </button>

        {status === 'success' ? (
          <div className="text-center py-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Mail className="text-green-600" size={24} />
            </div>
            <h3 className="text-lg font-bold text-gray-900">You're in!</h3>
            <p className="text-gray-500 mt-1">Check your inbox for weekly DevOps insights.</p>
          </div>
        ) : (
          <>
            <div className="text-center mb-5">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Mail className="text-blue-600" size={24} />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Stay ahead in DevOps</h2>
              <p className="text-gray-500 mt-1">
                Get weekly tool insights, comparison guides, and industry trends.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
              <button
                type="submit"
                disabled={status === 'loading'}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {status === 'loading' ? 'Subscribing...' : 'Subscribe — It\'s Free'}
              </button>
              {status === 'error' && (
                <p className="text-red-500 text-sm text-center">Something went wrong. Please try again.</p>
              )}
            </form>

            <p className="text-xs text-gray-400 text-center mt-3">No spam. Unsubscribe anytime.</p>
          </>
        )}
      </div>
    </div>
  );
};

export default EmailCaptureModal;
