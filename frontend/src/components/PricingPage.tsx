import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Zap, Shield, Users, Crown, Sparkles } from 'lucide-react';
import { API_BASE } from '../config';

/**
 * Subscription Plan Interface
 */
interface Plan {
    id: string;
    name: string;
    price: number;
    features: string[];
    limits: {
        daily_comparisons: number;
        saved_tools: number;
        api_calls: number;
    };
}

/**
 * PricingPage Component
 * 
 * Premium pricing page with subscription tier cards,
 * feature comparison, and Stripe checkout integration.
 */
const PricingPage: React.FC = () => {
    const navigate = useNavigate();
    const [plans, setPlans] = useState<Plan[]>([]);
    const [loading, setLoading] = useState(true);
    const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly');

    // Get auth token from localStorage
    const token = localStorage.getItem('token');

    useEffect(() => {
        fetchPlans();
    }, []);

    /**
     * Fetch available subscription plans from API
     */
    const fetchPlans = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/payments/plans`);
            if (response.ok) {
                const data = await response.json();
                setPlans(data);
            } else {
                throw new Error('Failed to fetch plans');
            }
        } catch (err) {
            console.error('Error fetching plans:', err);
            // Use default plans if API fails
            setPlans([
                {
                    id: 'free',
                    name: 'Free',
                    price: 0,
                    features: [
                        '3 tool comparisons per day',
                        'Basic search functionality',
                        'Community reviews access',
                        'Email support'
                    ],
                    limits: { daily_comparisons: 3, saved_tools: 10, api_calls: 0 }
                },
                {
                    id: 'pro',
                    name: 'Pro',
                    price: 9.99,
                    features: [
                        'Unlimited AI comparisons',
                        'Advanced analytics dashboard',
                        'Priority email support',
                        'Custom tool stacks',
                        'Export comparison reports',
                        'No ads'
                    ],
                    limits: { daily_comparisons: -1, saved_tools: 100, api_calls: 1000 }
                },
                {
                    id: 'enterprise',
                    name: 'Enterprise',
                    price: 29.99,
                    features: [
                        'Everything in Pro',
                        'Team management (up to 10 users)',
                        'API access',
                        'Custom integrations',
                        'Dedicated support',
                        'SSO integration',
                        'Advanced security features'
                    ],
                    limits: { daily_comparisons: -1, saved_tools: -1, api_calls: 10000 }
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Handle subscription checkout
     */
    const handleSubscribe = async (planId: string) => {
        if (!token) {
            // Redirect to login if not authenticated
            navigate('/login?redirect=/pricing');
            return;
        }

        if (planId === 'free') {
            navigate('/');
            return;
        }

        setCheckoutLoading(planId);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/payments/create-checkout-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ plan_id: planId })
            });

            if (response.ok) {
                const data = await response.json();
                // Redirect to Stripe Checkout
                window.location.href = data.checkout_url;
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create checkout session');
            }
        } catch (err: any) {
            console.error('Checkout error:', err);
            setError(err.message || 'Failed to start checkout process');
        } finally {
            setCheckoutLoading(null);
        }
    };

    /**
     * Get the icon for each plan
     */
    const getPlanIcon = (planId: string) => {
        switch (planId) {
            case 'free':
                return <Sparkles className="w-8 h-8 text-gray-500" />;
            case 'pro':
                return <Zap className="w-8 h-8 text-blue-500" />;
            case 'enterprise':
                return <Crown className="w-8 h-8 text-purple-500" />;
            default:
                return <Shield className="w-8 h-8 text-gray-500" />;
        }
    };

    /**
     * Get the style for each plan card
     */
    const getPlanStyle = (planId: string) => {
        switch (planId) {
            case 'pro':
                return 'border-blue-500 bg-gradient-to-br from-blue-50 to-white shadow-xl scale-105 relative z-10';
            case 'enterprise':
                return 'border-purple-500 bg-gradient-to-br from-purple-50 to-white';
            default:
                return 'border-gray-200 bg-white';
        }
    };

    /**
     * Get the button style for each plan
     */
    const getButtonStyle = (planId: string) => {
        switch (planId) {
            case 'pro':
                return 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg';
            case 'enterprise':
                return 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white shadow-lg';
            default:
                return 'bg-gray-100 hover:bg-gray-200 text-gray-700';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 text-white py-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h1 className="text-5xl font-bold mb-6">
                        Choose Your Plan
                    </h1>
                    <p className="text-xl text-blue-100 max-w-3xl mx-auto mb-8">
                        Unlock the full potential of CloudEngineered with our premium plans.
                        Get unlimited AI comparisons, advanced analytics, and priority support.
                    </p>

                    {/* Billing Toggle */}
                    <div className="flex items-center justify-center gap-4">
                        <span className={`text-sm ${billingPeriod === 'monthly' ? 'text-white' : 'text-blue-200'}`}>
                            Monthly
                        </span>
                        <button
                            onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
                            className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-400 transition-colors"
                        >
                            <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${billingPeriod === 'annual' ? 'translate-x-6' : 'translate-x-1'
                                    }`}
                            />
                        </button>
                        <span className={`text-sm ${billingPeriod === 'annual' ? 'text-white' : 'text-blue-200'}`}>
                            Annual
                            <span className="ml-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                                Save 20%
                            </span>
                        </span>
                    </div>
                </div>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                        {error}
                    </div>
                </div>
            )}

            {/* Pricing Cards */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
                    {plans.map((plan) => (
                        <div
                            key={plan.id}
                            className={`rounded-2xl border-2 p-8 transition-all duration-300 hover:shadow-lg ${getPlanStyle(plan.id)}`}
                        >
                            {/* Popular Badge */}
                            {plan.id === 'pro' && (
                                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-semibold px-4 py-1 rounded-full shadow-lg">
                                        Most Popular
                                    </span>
                                </div>
                            )}

                            {/* Plan Header */}
                            <div className="text-center mb-8">
                                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                                    {getPlanIcon(plan.id)}
                                </div>
                                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                                <div className="flex items-baseline justify-center">
                                    <span className="text-4xl font-extrabold text-gray-900">
                                        ${billingPeriod === 'annual' ? (plan.price * 0.8 * 12).toFixed(0) : plan.price}
                                    </span>
                                    <span className="text-gray-500 ml-2">
                                        /{billingPeriod === 'annual' ? 'year' : 'month'}
                                    </span>
                                </div>
                                {billingPeriod === 'annual' && plan.price > 0 && (
                                    <p className="text-sm text-green-600 mt-1">
                                        ${(plan.price * 12 - plan.price * 0.8 * 12).toFixed(0)} saved per year
                                    </p>
                                )}
                            </div>

                            {/* Features List */}
                            <ul className="space-y-4 mb-8">
                                {plan.features.map((feature, index) => (
                                    <li key={index} className="flex items-start">
                                        <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                                        <span className="text-gray-600">{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            {/* CTA Button */}
                            <button
                                onClick={() => handleSubscribe(plan.id)}
                                disabled={checkoutLoading === plan.id}
                                className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-200 ${getButtonStyle(plan.id)} ${checkoutLoading === plan.id ? 'opacity-75 cursor-not-allowed' : ''
                                    }`}
                            >
                                {checkoutLoading === plan.id ? (
                                    <span className="flex items-center justify-center">
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Processing...
                                    </span>
                                ) : plan.id === 'free' ? (
                                    'Get Started Free'
                                ) : (
                                    `Subscribe to ${plan.name}`
                                )}
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* FAQ Section */}
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
                    Frequently Asked Questions
                </h2>
                <div className="space-y-6">
                    <div className="bg-white rounded-xl p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Can I cancel my subscription anytime?
                        </h3>
                        <p className="text-gray-600">
                            Yes, you can cancel your subscription at any time. Your access will continue until the end of your current billing period.
                        </p>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            What payment methods do you accept?
                        </h3>
                        <p className="text-gray-600">
                            We accept all major credit cards (Visa, MasterCard, American Express) through our secure Stripe payment system.
                        </p>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Can I upgrade or downgrade my plan?
                        </h3>
                        <p className="text-gray-600">
                            Absolutely! You can upgrade or downgrade your plan at any time. Changes take effect immediately, and we'll prorate the difference.
                        </p>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Is there a free trial?
                        </h3>
                        <p className="text-gray-600">
                            Our Free tier gives you access to core features at no cost. When you're ready for more, upgrade to Pro or Enterprise.
                        </p>
                    </div>
                </div>
            </div>

            {/* Trust Section */}
            <div className="bg-gray-100 py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <div className="flex items-center justify-center gap-8 flex-wrap">
                        <div className="flex items-center gap-2 text-gray-600">
                            <Shield className="w-5 h-5 text-green-500" />
                            <span>Secure Payment</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-600">
                            <Users className="w-5 h-5 text-blue-500" />
                            <span>10,000+ Users</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-600">
                            <Zap className="w-5 h-5 text-yellow-500" />
                            <span>Instant Access</span>
                        </div>
                    </div>
                    <p className="mt-4 text-sm text-gray-500">
                        Powered by Stripe for secure, PCI-compliant payment processing.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default PricingPage;
