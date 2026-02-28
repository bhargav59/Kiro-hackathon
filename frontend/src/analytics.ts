import posthog from 'posthog-js';

let initialized = false;

/**
 * Initialize PostHog analytics.
 * Reads VITE_POSTHOG_KEY and VITE_POSTHOG_HOST from environment.
 */
export const initAnalytics = () => {
  const key = import.meta.env.VITE_POSTHOG_KEY;
  if (!key || initialized) return;

  posthog.init(key, {
    api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com',
    autocapture: true,
    capture_pageview: true,
    capture_pageleave: true,
    loaded: (ph) => {
      if (import.meta.env.DEV) ph.debug();
    },
  });
  initialized = true;
};

/**
 * Track a custom event.
 */
export const trackEvent = (event: string, properties?: Record<string, unknown>) => {
  if (!initialized) return;
  posthog.capture(event, properties);
};

/**
 * Identify a logged-in user.
 */
export const identifyUser = (userId: string, traits?: Record<string, unknown>) => {
  if (!initialized) return;
  posthog.identify(userId, traits);
};

/**
 * Reset user identity on logout.
 */
export const resetUser = () => {
  if (!initialized) return;
  posthog.reset();
};
