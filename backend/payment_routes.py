"""
Payment API Routes for CloudEngineered Platform

This module defines FastAPI routes for payment processing:
- Checkout session creation
- Webhook handling
- Subscription management
- Payment history
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Header
from pydantic import BaseModel
from typing import Optional
import sqlite3
from datetime import datetime
import os

from stripe_service import (
    stripe_service,
    get_plan_features,
    get_all_plans,
    SUBSCRIPTION_PLANS
)

# Create router
router = APIRouter(prefix="/api/payments", tags=["payments"])

# Database path
DB_PATH = "blog.db"

# Pydantic models for request/response
class CheckoutRequest(BaseModel):
    """Request model for creating a checkout session."""
    plan_id: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class SubscriptionResponse(BaseModel):
    """Response model for subscription status."""
    has_subscription: bool
    plan_id: str
    plan_name: str
    status: str
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False
    features: list


class PlanResponse(BaseModel):
    """Response model for subscription plans."""
    id: str
    name: str
    price: float
    features: list
    limits: dict


def init_payment_tables():
    """
    Initialize payment-related database tables.
    
    Creates tables for:
    - user_subscriptions: Track user subscription status
    - payment_history: Record payment transactions
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create user_subscriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            plan_id TEXT DEFAULT 'free',
            status TEXT DEFAULT 'active',
            current_period_start TIMESTAMP,
            current_period_end TIMESTAMP,
            cancel_at_period_end BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create payment_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stripe_payment_id TEXT,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            status TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    conn.close()


# Initialize tables on module load
init_payment_tables()


def get_user_from_token(authorization: str = Header(None)) -> Optional[dict]:
    """
    Extract user information from authorization token.
    
    Args:
        authorization: Bearer token from Authorization header
        
    Returns:
        User dictionary or None if invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    # Import from shared auth utilities
    from auth_utils import verify_token
    
    token = authorization.split(" ")[1]
    
    try:
        payload = verify_token(token)
        if not payload:
            return None
            
        user_id = payload.get("user_id")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {"id": row[0], "email": row[1], "username": row[2]}
        return None
        
    except Exception:
        return None


def get_user_subscription(user_id: int) -> dict:
    """
    Get user's current subscription details.
    
    Args:
        user_id: User ID
        
    Returns:
        Subscription details dictionary
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT plan_id, status, stripe_subscription_id, 
               current_period_end, cancel_at_period_end
        FROM user_subscriptions 
        WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        plan = SUBSCRIPTION_PLANS.get(row[0], SUBSCRIPTION_PLANS["free"])
        return {
            "has_subscription": row[0] != "free",
            "plan_id": row[0],
            "plan_name": plan["name"],
            "status": row[1],
            "stripe_subscription_id": row[2],
            "current_period_end": row[3],
            "cancel_at_period_end": bool(row[4]),
            "features": plan["features"]
        }
    
    # Default to free plan
    free_plan = SUBSCRIPTION_PLANS["free"]
    return {
        "has_subscription": False,
        "plan_id": "free",
        "plan_name": "Free",
        "status": "active",
        "stripe_subscription_id": None,
        "current_period_end": None,
        "cancel_at_period_end": False,
        "features": free_plan["features"]
    }


@router.get("/plans")
async def list_plans():
    """
    Get all available subscription plans.
    
    Returns:
        List of subscription plans with features and pricing
    """
    return get_all_plans()


@router.get("/subscription-status")
async def get_subscription_status(authorization: str = Header(None)):
    """
    Get current user's subscription status.
    
    Requires authentication.
    
    Returns:
        Current subscription details including plan, status, and features
    """
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    subscription = get_user_subscription(user["id"])
    return subscription


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    authorization: str = Header(None)
):
    """
    Create a Stripe Checkout session for subscription.
    
    Args:
        request: Checkout request with plan_id and redirect URLs
        
    Returns:
        Checkout session URL to redirect user to Stripe
    """
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Validate plan
    if request.plan_id not in ["pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan. Choose 'pro' or 'enterprise'")
    
    if not stripe_service.is_configured():
        raise HTTPException(
            status_code=503, 
            detail="Payment system not configured. Please contact support."
        )
    
    # Get or create Stripe customer
    customer_id = stripe_service.get_or_create_customer(
        user_id=user["id"],
        email=user["email"],
        name=user["username"]
    )
    
    if not customer_id:
        raise HTTPException(status_code=500, detail="Failed to create customer record")
    
    # Store customer ID in database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_subscriptions (user_id, stripe_customer_id, plan_id)
        VALUES (?, ?, 'free')
        ON CONFLICT(user_id) DO UPDATE SET stripe_customer_id = ?
    """, (user["id"], customer_id, customer_id))
    conn.commit()
    conn.close()
    
    # Create checkout session
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    success_url = request.success_url or f"{base_url}/checkout/success"
    cancel_url = request.cancel_url or f"{base_url}/pricing"
    
    session = stripe_service.create_checkout_session(
        customer_id=customer_id,
        plan_id=request.plan_id,
        success_url=success_url,
        cancel_url=cancel_url,
        user_id=user["id"]
    )
    
    if not session:
        raise HTTPException(status_code=500, detail="Failed to create checkout session")
    
    return {"checkout_url": session["url"], "session_id": session["session_id"]}


@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    Processes events like:
    - checkout.session.completed
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    event = stripe_service.verify_webhook_signature(payload, signature)
    
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event["type"]
    data = event["data"]["object"]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if event_type == "checkout.session.completed":
            # Subscription created successfully
            user_id = data.get("metadata", {}).get("user_id")
            plan_id = data.get("metadata", {}).get("plan_id")
            subscription_id = data.get("subscription")
            customer_id = data.get("customer")
            
            if user_id and subscription_id:
                # Get subscription details from Stripe
                sub_details = stripe_service.get_subscription(subscription_id)
                
                cursor.execute("""
                    INSERT INTO user_subscriptions 
                    (user_id, stripe_customer_id, stripe_subscription_id, plan_id, status,
                     current_period_start, current_period_end)
                    VALUES (?, ?, ?, ?, 'active', ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        stripe_subscription_id = ?,
                        plan_id = ?,
                        status = 'active',
                        current_period_start = ?,
                        current_period_end = ?,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_id, customer_id, subscription_id, plan_id,
                    sub_details["current_period_start"] if sub_details else None,
                    sub_details["current_period_end"] if sub_details else None,
                    subscription_id, plan_id,
                    sub_details["current_period_start"] if sub_details else None,
                    sub_details["current_period_end"] if sub_details else None
                ))
        
        elif event_type == "customer.subscription.updated":
            subscription_id = data.get("id")
            status = data.get("status")
            cancel_at_period_end = data.get("cancel_at_period_end", False)
            
            cursor.execute("""
                UPDATE user_subscriptions 
                SET status = ?, cancel_at_period_end = ?, updated_at = CURRENT_TIMESTAMP
                WHERE stripe_subscription_id = ?
            """, (status, cancel_at_period_end, subscription_id))
        
        elif event_type == "customer.subscription.deleted":
            subscription_id = data.get("id")
            
            cursor.execute("""
                UPDATE user_subscriptions 
                SET status = 'cancelled', plan_id = 'free', updated_at = CURRENT_TIMESTAMP
                WHERE stripe_subscription_id = ?
            """, (subscription_id,))
        
        elif event_type == "invoice.payment_succeeded":
            customer_id = data.get("customer")
            amount = data.get("amount_paid", 0) / 100
            
            # Find user by customer ID
            cursor.execute(
                "SELECT user_id FROM user_subscriptions WHERE stripe_customer_id = ?",
                (customer_id,)
            )
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    INSERT INTO payment_history 
                    (user_id, stripe_payment_id, amount, status, description)
                    VALUES (?, ?, ?, 'succeeded', 'Subscription payment')
                """, (row[0], data.get("id"), amount))
        
        elif event_type == "invoice.payment_failed":
            customer_id = data.get("customer")
            
            cursor.execute("""
                UPDATE user_subscriptions 
                SET status = 'past_due', updated_at = CURRENT_TIMESTAMP
                WHERE stripe_customer_id = ?
            """, (customer_id,))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")
    finally:
        conn.close()
    
    return {"status": "success"}


@router.post("/cancel-subscription")
async def cancel_subscription(authorization: str = Header(None)):
    """
    Cancel the current user's subscription.
    
    Subscription will remain active until the end of the current billing period.
    """
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    subscription = get_user_subscription(user["id"])
    
    if not subscription.get("stripe_subscription_id"):
        raise HTTPException(status_code=400, detail="No active subscription to cancel")
    
    success = stripe_service.cancel_subscription(
        subscription["stripe_subscription_id"],
        immediate=False
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    
    # Update database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_subscriptions 
        SET cancel_at_period_end = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (user["id"],))
    conn.commit()
    conn.close()
    
    return {
        "message": "Subscription will be cancelled at the end of the billing period",
        "current_period_end": subscription.get("current_period_end")
    }


@router.get("/payment-history")
async def get_payment_history(authorization: str = Header(None), limit: int = 10):
    """
    Get payment history for the current user.
    
    Args:
        limit: Maximum number of payments to return (default: 10)
        
    Returns:
        List of payment records
    """
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT stripe_payment_id, amount, currency, status, description, created_at
        FROM payment_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user["id"], limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "amount": row[1],
        "currency": row[2],
        "status": row[3],
        "description": row[4],
        "created_at": row[5]
    } for row in rows]


@router.post("/create-portal-session")
async def create_portal_session(authorization: str = Header(None)):
    """
    Create a Stripe Customer Portal session for subscription management.
    
    Allows users to:
    - Update payment methods
    - View invoices
    - Manage subscription
    """
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT stripe_customer_id FROM user_subscriptions WHERE user_id = ?",
        (user["id"],)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        raise HTTPException(status_code=400, detail="No customer record found")
    
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    portal_url = stripe_service.create_portal_session(
        customer_id=row[0],
        return_url=f"{base_url}/subscription"
    )
    
    if not portal_url:
        raise HTTPException(status_code=500, detail="Failed to create portal session")
    
    return {"portal_url": portal_url}
