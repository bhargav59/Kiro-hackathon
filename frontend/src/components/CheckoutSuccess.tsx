import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { CheckCircle, ArrowRight, Sparkles, Zap, Crown } from 'lucide-react';
import { API_BASE } from '../config';

/**
 * CheckoutSuccess Component
 * 
 * Post-payment success page displayed after completing Stripe checkout.
 * Shows confirmation and guides user to next steps.
 */
const CheckoutSuccess: React.FC = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const [loading, setLoading] = useState(true);
    const [planName, setPlanName] = useState<string>('Pro');

    const sessionId = searchParams.get('session_id');
    const token = localStorage.getItem('token');

    useEffect(() => {
        // Verify the subscription was created successfully
        const verifySubscription = async () => {
            if (!token) {
                navigate('/login');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/payments/subscription-status`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    setPlanName(data.plan_name);
                }
            } catch (error) {
                console.error('Error verifying subscription:', error);
            } finally {
                setLoading(false);
            }
        };

        // Small delay to allow webhook to process
        setTimeout(verifySubscription, 2000);
    }, [token, sessionId, navigate]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Confirming your subscription...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
            <div className="max-w-3xl mx-auto px-4 py-20">
                {/* Success Animation */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-green-100 mb-6 animate-bounce">
                        <CheckCircle className="w-12 h-12 text-green-600" />
                    </div>
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Welcome to {planName}! 🎉
                    </h1>
                    <p className="text-xl text-gray-600 max-w-lg mx-auto">
                        Your subscription is now active. You have access to all premium features.
                    </p>
                </div>

                {/* Order Summary Card */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8">
                    <div className="flex items-center justify-between mb-6 pb-6 border-b border-gray-200">
                        <div className="flex items-center gap-4">
                            <div className={`p-3 rounded-xl ${planName === 'Enterprise' ? 'bg-purple-100' : 'bg-blue-100'}`}>
                                {planName === 'Enterprise' ? (
                                    <Crown className="w-8 h-8 text-purple-600" />
                                ) : (
                                    <Zap className="w-8 h-8 text-blue-600" />
                                )}
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-gray-900">{planName} Plan</h2>
                                <p className="text-gray-500">Monthly subscription</p>
                            </div>
                        </div>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                            Active
                        </span>
                    </div>

                    <div className="space-y-3 text-gray-600">
                        <p className="flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-green-500" />
                            Payment confirmed successfully
                        </p>
                        <p className="flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-green-500" />
                            Premium features activated instantly
                        </p>
                        <p className="flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-green-500" />
                            Receipt sent to your email
                        </p>
                    </div>
                </div>

                {/* Next Steps */}
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white mb-8">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Sparkles className="w-6 h-6" />
                        What's Next?
                    </h3>
                    <ul className="space-y-3 mb-6">
                        <li className="flex items-start gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-sm font-medium">1</span>
                            <span>Explore unlimited AI-powered tool comparisons</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-sm font-medium">2</span>
                            <span>Access advanced analytics dashboard</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-sm font-medium">3</span>
                            <span>Build custom tool stacks for your projects</span>
                        </li>
                    </ul>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        to="/compare"
                        className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg"
                    >
                        Start Comparing Tools
                        <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link
                        to="/subscription"
                        className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-all"
                    >
                        Manage Subscription
                    </Link>
                </div>

                {/* Help Section */}
                <div className="text-center mt-12 text-gray-500 text-sm">
                    <p>
                        Need help? Contact our{' '}
                        <a href="mailto:support@cloudengineered.com" className="text-blue-600 hover:underline">
                            support team
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default CheckoutSuccess;
