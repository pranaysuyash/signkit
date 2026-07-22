(function () {
  'use strict';

  const config = window.SignKitCheckoutConfig || {};
  const productId = String(config.dodoProductId || '').trim();
  const hasDodoCheckout = /^pdt_[A-Za-z0-9]+$/.test(productId);
  const dodoUrl = hasDodoCheckout
    ? `${config.dodoBaseUrl}${encodeURIComponent(productId)}`
    : '';

  function trackCheckout(provider, placement) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'checkout_intent', {
        event_category: 'conversion',
        checkout_provider: provider,
        placement,
        value: 1,
      });
    }
  }

  function configureCheckoutLinks() {
    document.querySelectorAll('[data-checkout-provider="dodo"]').forEach((link) => {
      if (hasDodoCheckout) {
        link.href = dodoUrl;
        link.removeAttribute('aria-disabled');
        link.classList.remove('checkout-unavailable');
      } else {
        link.removeAttribute('href');
        link.setAttribute('aria-disabled', 'true');
        link.classList.add('checkout-unavailable');
        link.title = 'Dodo checkout will be enabled when the SignKit product ID is configured.';
      }

      link.addEventListener('click', (event) => {
        if (!hasDodoCheckout) {
          event.preventDefault();
          document.querySelector('[data-checkout-configuration-note]')?.focus();
          return;
        }
        trackCheckout('dodo', link.dataset.checkoutPlacement || 'unknown');
      });
    });

    document.querySelectorAll('[data-checkout-provider="gumroad"]').forEach((link) => {
      link.href = config.gumroadUrl;
      link.addEventListener('click', () => {
        trackCheckout('gumroad', link.dataset.checkoutPlacement || 'fallback');
      });
    });

    document.documentElement.dataset.dodoCheckout = hasDodoCheckout ? 'configured' : 'missing';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', configureCheckoutLinks);
  } else {
    configureCheckoutLinks();
  }
})();
