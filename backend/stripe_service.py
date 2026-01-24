"""
Stripe Payment Integration Service for CloudEngineered Platform

This module handles all Stripe-related operations including:
- Checkout session creation
- Webhook event processing
- Subscription management
- Customer management
"""

import os
import stripe
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

# Subscription plan configurations
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "stripe_price_id": None,
        "features": [
            "3 tool comparisons per day",
            "Basic search functionality",
            "Community reviews access",
            "Email support"
        ],
        "limits": {
            "daily_comparisons": 3,
            "saved_tools": 10,
            "api_calls": 0
        }
    },
    "pro": {
        "name": "Pro",
        "price": 999,  # $9.99 in cents
        "stripe_price_id": os.getenv("STRIPE_PRICE_PRO_MONTHLY"),
        "features": [
            "Unlimited AI comparisons",
            "Advanced analytics dashboard",
            "Priority email support",
            "Custom tool stacks",
            "Export comparison reports",
            "No ads"
        ],
        "limits": {
            "daily_comparisons": -1,  # unlimited
            "saved_tools": 100,
            "api_calls": 1000
        }
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 2999,  # $29.99 in cents
        "stripe_price_id": os.getenv("STRIPE_PRICE_ENTERPRISE_MONTHLY"),
        "features": [
            "Everything in Pro",
            "Team management (up to 10 users)",
            "API access",
            "Custom integrations",
            "Dedicated support",
            "SSO integration",
            "Advanced security features"
        ],
        "limits": {
            "daily_comparisons": -1,
            "saved_tools": -1,
            "api_calls": 10000
        }
    }
}


class StripeService:
    """
    Service class for handling Stripe payment operations.
    
    This class provides methods for:
    - Creating checkout sessions for subscriptions
    - Managing customer records
    - Processing webhook events
    - Handling subscription lifecycle
    """
    
    def __init__(self):
        """Initialize the Stripe service with API configuration."""
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        if not stripe.api_key:
            logger.warning("STRIPE_SECRET_KEY not configured. Payment features will be disabled.")
    
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(stripe.api_key)
    
    def get_or_create_customer(self, user_id: int, email: str, name: str = None) -> Optional[str]:
        """
        Get existing Stripe customer or create a new one.
        
        Args:
            user_id: Internal user ID
            email: User's email address
            name: User's display name
            
        Returns:
            Stripe customer ID or None if creation fails
        """
        if not self.is_configured():
            return None
            
        try:
            # Search for existing customer by email
            customers = stripe.Customer.search(
                query=f"email:'{email}'"
            )
            
            if customers.data:
                return customers.data[0].id
            
            # Create new customer
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": str(user_id)}
            )
            
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None
    
    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe Checkout session for subscription.
        
        Args:
            customer_id: Stripe customer ID
            plan_id: Plan identifier (pro, enterprise)
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            user_id: Internal user ID for metadata
            
        Returns:
            Dictionary with session_id and url, or None if creation fails
        """
        if not self.is_configured():
            return None
            
        plan = SUBSCRIPTION_PLANS.get(plan_id)
        if not plan or not plan.get("stripe_price_id"):
            logger.error(f"Invalid plan or missing price ID: {plan_id}")
            return None
        
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": plan["stripe_price_id"],
                    "quantity": 1
                }],
                mode="subscription",
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user_id),
                    "plan_id": plan_id
                },
                subscription_data={
                    "metadata": {
                        "user_id": str(user_id),
                        "plan_id": plan_id
                    }
                }
            )
            
            logger.info(f"Created checkout session {session.id} for user {user_id}")
            return {
                "session_id": session.id,
                "url": session.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            return None
    
    def create_portal_session(self, customer_id: str, return_url: str) -> Optional[str]:
        """
        Create a Stripe Customer Portal session for subscription management.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to redirect after portal session
            
        Returns:
            Portal session URL or None if creation fails
        """
        if not self.is_configured():
            return None
            
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            immediate: If True, cancel immediately. Otherwise, cancel at period end.
            
        Returns:
            True if cancellation successful, False otherwise
        """
        if not self.is_configured():
            return False
            
        try:
            if immediate:
                stripe.Subscription.delete(subscription_id)
            else:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            logger.info(f"Cancelled subscription {subscription_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription details from Stripe.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription details dictionary or None
        """
        if not self.is_configured():
            return None
            
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan_id": subscription.metadata.get("plan_id", "pro")
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription: {e}")
            return None
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """
        Verify webhook signature and parse event.
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header value
            
        Returns:
            Parsed event object or None if verification fails
        """
        if not self.webhook_secret:
            logger.error("Webhook secret not configured")
            return None
            
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return None
    
    def get_payment_history(self, customer_id: str, limit: int = 10) -> list:
        """
        Get payment history for a customer.
        
        Args:
            customer_id: Stripe customer ID
            limit: Maximum number of payments to return
            
        Returns:
            List of payment records
        """
        if not self.is_configured():
            return []
            
        try:
            payments = stripe.PaymentIntent.list(
                customer=customer_id,
                limit=limit
            )
            
            return [{
                "id": payment.id,
                "amount": payment.amount / 100,  # Convert cents to dollars
                "currency": payment.currency.upper(),
                "status": payment.status,
                "created": datetime.fromtimestamp(payment.created).isoformat(),
                "description": payment.description or "Subscription payment"
            } for payment in payments.data]
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get payment history: {e}")
            return []


# Create singleton instance
stripe_service = StripeService()


def get_plan_features(plan_id: str) -> Dict[str, Any]:
    """
    Get features and limits for a subscription plan.
    
    Args:
        plan_id: Plan identifier (free, pro, enterprise)
        
    Returns:
        Plan details dictionary
    """
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    return {
        "id": plan_id,
        "name": plan["name"],
        "price": plan["price"] / 100 if plan["price"] > 0 else 0,
        "features": plan["features"],
        "limits": plan["limits"]
    }


def get_all_plans() -> list:
    """
    Get all available subscription plans.
    
    Returns:
        List of plan details
    """
    return [get_plan_features(plan_id) for plan_id in SUBSCRIPTION_PLANS.keys()]
