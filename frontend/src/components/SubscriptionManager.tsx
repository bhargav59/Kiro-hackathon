import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    CreditCard,
    Calendar,
    CheckCircle,
    AlertCircle,
    Settings,
    ArrowRight,
    RefreshCw,
    XCircle,
    Crown,
    Zap
} from 'lucide-react';
import { API_BASE } from '../config';

/**
 * Subscription Status Interface
 */
interface SubscriptionStatus {
    has_subscription: boolean;
    plan_id: string;
    plan_name: string;
    status: string;
    current_period_end: string | null;
    cancel_at_period_end: boolean;
    features: string[];
}

/**
 * Payment History Item Interface
 */
interface PaymentItem {
    id: string;
    amount: number;
    currency: string;
    status: string;
    description: string;
    created_at: string;
}

/**
 * SubscriptionManager Component
 * 
 * Allows users to view and manage their subscription:
 * - Current plan status
 * - Payment history
 * - Upgrade/downgrade options
 * - Cancel subscription
 */
const SubscriptionManager: React.FC = () => {
    const navigate = useNavigate();
    const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
    const [payments, setPayments] = useState<PaymentItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [cancelLoading, setCancelLoading] = useState(false);
    const [portalLoading, setPortalLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showCancelConfirm, setShowCancelConfirm] = useState(false);

    const token = localStorage.getItem('token');

    useEffect(() => {
        if (!token) {
            navigate('/login?redirect=/subscription');
            return;
        }
        fetchSubscriptionData();
    }, [token, navigate]);

    /**
     * Fetch subscription status and payment history
     */
    const fetchSubscriptionData = async () => {
        try {
            // Fetch subscription status
            const subResponse = await fetch(`${API_BASE}/api/payments/subscription-status`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (subResponse.ok) {
                const subData = await subResponse.json();
                setSubscription(subData);
            } else if (subResponse.status === 401) {
                navigate('/login?redirect=/subscription');
                return;
            }

            // Fetch payment history
            const payResponse = await fetch(`${API_BASE}/api/payments/payment-history`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (payResponse.ok) {
                const payData = await payResponse.json();
                setPayments(payData);
            }
        } catch (err) {
            console.error('Error fetching subscription data:', err);
            setError('Failed to load subscription data');
        } finally {
            setLoading(false);
        }
    };

    /**
     * Handle subscription cancellation
     */
    const handleCancelSubscription = async () => {
        setCancelLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/payments/cancel-subscription`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                await fetchSubscriptionData();
                setShowCancelConfirm(false);
            } else {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to cancel subscription');
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setCancelLoading(false);
        }
    };

    /**
     * Open Stripe Customer Portal for billing management
     */
    const handleManageBilling = async () => {
        setPortalLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/payments/create-portal-session`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                window.location.href = data.portal_url;
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to open billing portal');
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setPortalLoading(false);
        }
    };

    /**
     * Get the status badge color and icon
     */
    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'active':
                return { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="w-4 h-4" /> };
            case 'past_due':
                return { color: 'bg-yellow-100 text-yellow-800', icon: <AlertCircle className="w-4 h-4" /> };
            case 'cancelled':
                return { color: 'bg-red-100 text-red-800', icon: <XCircle className="w-4 h-4" /> };
            default:
                return { color: 'bg-gray-100 text-gray-800', icon: <RefreshCw className="w-4 h-4" /> };
        }
    };

    /**
     * Format date for display
     */
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-12">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Subscription Management</h1>
                    <p className="text-gray-600 mt-2">Manage your subscription and billing</p>
                </div>

                {/* Error Alert */}
                {error && (
                    <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        {error}
                    </div>
                )}

                {/* Current Plan Card */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8">
                    <div className="flex items-start justify-between mb-6">
                        <div className="flex items-center gap-4">
                            <div className={`p-3 rounded-xl ${subscription?.plan_id === 'enterprise' ? 'bg-purple-100' : subscription?.plan_id === 'pro' ? 'bg-blue-100' : 'bg-gray-100'}`}>
                                {subscription?.plan_id === 'enterprise' ? (
                                    <Crown className="w-8 h-8 text-purple-600" />
                                ) : subscription?.plan_id === 'pro' ? (
                                    <Zap className="w-8 h-8 text-blue-600" />
                                ) : (
                                    <CreditCard className="w-8 h-8 text-gray-600" />
                                )}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">{subscription?.plan_name} Plan</h2>
                                <div className="flex items-center gap-2 mt-1">
                                    {subscription && (
                                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(subscription.status).color}`}>
                                            {getStatusBadge(subscription.status).icon}
                                            {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
                                        </span>
                                    )}
                                    {subscription?.cancel_at_period_end && (
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                                            Cancels at period end
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Billing Period Info */}
                    {subscription?.current_period_end && (
                        <div className="flex items-center gap-2 text-gray-600 mb-6">
                            <Calendar className="w-5 h-5" />
                            <span>
                                {subscription.cancel_at_period_end ? 'Access ends' : 'Next billing date'}:{' '}
                                <strong>{formatDate(subscription.current_period_end)}</strong>
                            </span>
                        </div>
                    )}

                    {/* Features List */}
                    <div className="border-t border-gray-200 pt-6 mb-6">
                        <h3 className="text-sm font-semibold text-gray-900 mb-3">Your Plan Features</h3>
                        <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {subscription?.features.map((feature, index) => (
                                <li key={index} className="flex items-center gap-2 text-gray-600 text-sm">
                                    <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                                    {feature}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-wrap gap-4">
                        {subscription?.plan_id === 'free' ? (
                            <Link
                                to="/pricing"
                                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg"
                            >
                                Upgrade Now
                                <ArrowRight className="w-5 h-5" />
                            </Link>
                        ) : (
                            <>
                                <button
                                    onClick={handleManageBilling}
                                    disabled={portalLoading}
                                    className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-all"
                                >
                                    <Settings className="w-5 h-5" />
                                    {portalLoading ? 'Loading...' : 'Manage Billing'}
                                </button>

                                {!subscription?.cancel_at_period_end && (
                                    <button
                                        onClick={() => setShowCancelConfirm(true)}
                                        className="inline-flex items-center gap-2 px-6 py-3 text-red-600 hover:bg-red-50 rounded-xl font-semibold transition-all"
                                    >
                                        Cancel Subscription
                                    </button>
                                )}
                            </>
                        )}
                    </div>
                </div>

                {/* Payment History */}
                {payments.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-6">Payment History</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-gray-200">
                                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Date</th>
                                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Description</th>
                                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Amount</th>
                                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {payments.map((payment) => (
                                        <tr key={payment.id} className="border-b border-gray-100 hover:bg-gray-50">
                                            <td className="py-3 px-4 text-sm text-gray-600">
                                                {formatDate(payment.created_at)}
                                            </td>
                                            <td className="py-3 px-4 text-sm text-gray-900">
                                                {payment.description}
                                            </td>
                                            <td className="py-3 px-4 text-sm font-medium text-gray-900">
                                                ${payment.amount.toFixed(2)} {payment.currency}
                                            </td>
                                            <td className="py-3 px-4">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${payment.status === 'succeeded' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {payment.status}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Cancel Confirmation Modal */}
                {showCancelConfirm && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-2xl max-w-md w-full p-8">
                            <h3 className="text-xl font-bold text-gray-900 mb-4">Cancel Subscription?</h3>
                            <p className="text-gray-600 mb-6">
                                Your subscription will remain active until the end of the current billing period.
                                After that, you'll be downgraded to the free plan.
                            </p>
                            <div className="flex gap-4">
                                <button
                                    onClick={() => setShowCancelConfirm(false)}
                                    className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-all"
                                >
                                    Keep Subscription
                                </button>
                                <button
                                    onClick={handleCancelSubscription}
                                    disabled={cancelLoading}
                                    className="flex-1 px-6 py-3 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-all disabled:opacity-50"
                                >
                                    {cancelLoading ? 'Cancelling...' : 'Yes, Cancel'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SubscriptionManager;
