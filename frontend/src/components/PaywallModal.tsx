import React from 'react';
import { Link } from 'react-router-dom';
import { X, Zap, Lock } from 'lucide-react';
import { trackEvent } from '../analytics';

interface PaywallModalProps {
  isOpen: boolean;
  onClose: () => void;
  feature: string;
}

const PaywallModal: React.FC<PaywallModalProps> = ({ isOpen, onClose, feature }) => {
  if (!isOpen) return null;

  trackEvent('paywall_shown', { feature });

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X size={20} />
        </button>

        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Lock className="text-blue-600" size={24} />
          </div>
          <h2 className="text-xl font-bold text-gray-900">Upgrade to Pro</h2>
          <p className="text-gray-500 mt-1">
            {feature === 'export'
              ? 'Comparison exports require a Pro plan'
              : `You've reached your daily ${feature} limit`}
          </p>
        </div>

        <div className="space-y-3 mb-6">
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Zap className="text-blue-500 mt-0.5 flex-shrink-0" size={18} />
            <div>
              <p className="font-medium text-gray-900">Unlimited AI Comparisons</p>
              <p className="text-sm text-gray-500">Compare any tools without daily limits</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Zap className="text-blue-500 mt-0.5 flex-shrink-0" size={18} />
            <div>
              <p className="font-medium text-gray-900">Export Reports</p>
              <p className="text-sm text-gray-500">Download comparison reports in Markdown & JSON</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Zap className="text-blue-500 mt-0.5 flex-shrink-0" size={18} />
            <div>
              <p className="font-medium text-gray-900">Unlimited AI Search</p>
              <p className="text-sm text-gray-500">Natural language search with no restrictions</p>
            </div>
          </div>
        </div>

        <Link
          to="/pricing"
          onClick={() => { trackEvent('paywall_upgrade_clicked', { feature }); onClose(); }}
          className="block w-full text-center bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          View Plans — Starting at $9.99/mo
        </Link>

        <button onClick={onClose} className="block w-full text-center text-gray-500 mt-3 text-sm hover:text-gray-700">
          Maybe later
        </button>
      </div>
    </div>
  );
};

export default PaywallModal;
