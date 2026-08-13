(function () {
  'use strict';

  const config = window.SignKitCheckoutConfig || {};
  const productId = String(config.dodoProductId || '').trim();
  const hasDodoCheckout = /^pdt_[A-Za-z0-9]+$/.test(productId);
  const dodoUrl = hasDodoCheckout
    ? `${config.dodoBaseUrl}${encodeURIComponent(productId)}`
    : '';
  const gumroadUrl = validHttpsUrl(config.gumroadUrl);

  function validHttpsUrl(value) {
    try {
      const url = new URL(String(value || ''));
      return url.protocol === 'https:' ? url.href : '';
    } catch (_error) {
      return '';
    }
  }

  function getEntryAttribution() {
    const params = new URLSearchParams(window.location.search);
    const attribution = {
      entry_path: window.location.pathname || '/',
    };

    for (const key of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content']) {
      const value = params.get(key);
      if (value) {
        attribution[key] = value.slice(0, 160);
      }
    }

    return attribution;
  }

  function trackCheckout(provider, placement) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'checkout_intent', {
        event_category: 'conversion',
        checkout_provider: provider,
        placement,
        value: 1,
        ...getEntryAttribution(),
      });
    }
  }

  function setCheckoutRole(link, role) {
    link.dataset.checkoutRole = role;
    link.classList.remove('checkout-primary', 'checkout-fallback', 'checkout-unavailable');
    link.classList.add(`checkout-${role}`);
    const label = link.querySelector?.('[data-checkout-label]');
    const labelText = role === 'primary'
      ? link.dataset.checkoutPrimaryLabel
      : link.dataset.checkoutFallbackLabel;
    if (label && labelText) {
      label.textContent = labelText;
    }
  }

  function disableCheckoutLink(link, title) {
    link.href = '';
    link.setAttribute('role', 'button');
    link.setAttribute('aria-disabled', 'true');
    link.title = title;
    setCheckoutRole(link, 'unavailable');
  }

  function enableCheckoutLink(link, url, role) {
    link.href = url;
    link.removeAttribute('role');
    link.removeAttribute('aria-disabled');
    link.removeAttribute('title');
    setCheckoutRole(link, role);
  }

  function focusConfigurationNote() {
    document.querySelector('[data-checkout-configuration-note]')?.focus();
  }

  function configureCheckoutLinks() {
    document.querySelectorAll('[data-checkout-provider="dodo"]').forEach((link) => {
      if (hasDodoCheckout) {
        enableCheckoutLink(link, dodoUrl, 'primary');
      } else {
        disableCheckoutLink(
          link,
          'Dodo checkout is unavailable until a valid SignKit product ID is configured.',
        );
      }

      link.addEventListener('click', (event) => {
        if (!hasDodoCheckout) {
          event.preventDefault();
          focusConfigurationNote();
          return;
        }
        trackCheckout('dodo', link.dataset.checkoutPlacement || 'unknown');
      });
    });

    document.querySelectorAll('[data-checkout-provider="gumroad"]').forEach((link) => {
      if (gumroadUrl) {
        enableCheckoutLink(link, gumroadUrl, hasDodoCheckout ? 'fallback' : 'primary');
      } else {
        disableCheckoutLink(link, 'Gumroad checkout is unavailable until its URL is configured.');
      }
      link.addEventListener('click', () => {
        if (gumroadUrl) {
          trackCheckout('gumroad', link.dataset.checkoutPlacement || 'fallback');
        }
      });
    });

    document.documentElement.dataset.dodoCheckout = hasDodoCheckout ? 'configured' : 'missing';
    document.documentElement.dataset.checkoutProvider = hasDodoCheckout
      ? 'dodo'
      : gumroadUrl
        ? 'gumroad'
        : 'unavailable';
    document.documentElement.dataset.checkoutState = hasDodoCheckout
      ? 'dodo-primary'
      : gumroadUrl
        ? 'gumroad-primary'
        : 'unavailable';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', configureCheckoutLinks);
  } else {
    configureCheckoutLinks();
  }
})();
