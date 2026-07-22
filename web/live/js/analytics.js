/*
 * Landing Page Analytics Helpers
 * - Real user detection
 * - Bot detection
 * - Scroll depth tracking
 * - CTA click tracking and UTM appending
 * - Session quality scoring
 *
 * Note: This file assumes gtag() is defined on the page. If not, calls fall back to console logs.
 */

(function () {
  // Safe wrapper for gtag and set user properties
  function safeGtag() {
    if (typeof gtag === 'function') {
      gtag.apply(null, arguments);
    } else {
      console.debug('gtag missing, REMOTE_EVENT:', arguments);
    }
  }

  // ---- Simple Bot Detection ----
  function isLikelyBot() {
    try {
      const ua = ((navigator && navigator.userAgent) || '').toLowerCase();
      const botPatterns = [
        'bot',
        'crawler',
        'spider',
        'scraper',
        'facebookexternalhit',
        'twitterbot',
        'linkedinbot',
        'slackbot',
        'discordbot',
        'telegrambot',
        'whatsapp',
        'preview',
        'prerender',
        'headless',
        'phantom',
        'selenium',
      ];
      for (let p of botPatterns) {
        if (ua.includes(p)) {
          return true;
        }
      }
      // headless / webdriver flags
      if (navigator && navigator.webdriver) return true;
      // no plugins and not a real browser
      if (
        !navigator.plugins ||
        (navigator.plugins && navigator.plugins.length === 0)
      ) {
        if (!navigator.webdriver) {
          return true;
        }
      }
    } catch (e) {
      console.debug('Bot detection error', e);
    }
    return false;
  }

  if (isLikelyBot()) {
    safeGtag('set', 'user_properties', { user_type: 'bot_or_crawler' });
    safeGtag('event', 'bot_detected', {
      event_category: 'traffic_quality',
      event_label: ((navigator && navigator.userAgent) || '').substr(0, 100),
    });
    // We exit early: avoid sending engagement events for suspected bots
    return; // Prevent other engagement events from firing for bots
  }

  // ---- Real User Detection ----
  window.pageLoadTime = Date.now();
  window.realUserDetected = false;
  window.mouseMoveCount = 0;
  window.scrollCount = 0;
  window.clickCount = 0;
  window.maxScroll = 0;

  function markRealUser() {
    if (window.realUserDetected) return;
    window.realUserDetected = true;
    safeGtag('event', 'real_user_detected', {
      event_category: 'engagement',
      event_label: 'human_interaction',
      value: 1,
    });
    safeGtag('set', 'user_properties', { user_type: 'real_human' });
    console.info('✅ Real user detected');
  }

  // Detect interactions
  document.addEventListener(
    'mousemove',
    function () {
      window.mouseMoveCount++;
      if (window.mouseMoveCount > 3) markRealUser();
    },
    { passive: true }
  );

  document.addEventListener(
    'scroll',
    function () {
      window.scrollCount++;
      if (window.scrollCount > 2) markRealUser();
    },
    { passive: true }
  );

  document.addEventListener('click', function () {
    window.clickCount++;
    markRealUser();
  });

  document.addEventListener('keydown', function () {
    markRealUser();
  });
  document.addEventListener('touchstart', function () {
    markRealUser();
  });

  setTimeout(function () {
    if (document.hasFocus && document.hasFocus()) markRealUser();
  }, 3000);

  // ---- Scroll depth tracking ----
  var scrollTimeout;
  var milestones = [25, 50, 75, 90, 100];
  var reached = {};
  function trackScroll() {
    try {
      var scrollPercent = Math.round(
        (window.scrollY /
          (document.documentElement.scrollHeight - window.innerHeight)) *
          100
      );
      if (scrollPercent > window.maxScroll) window.maxScroll = scrollPercent;
      milestones.forEach(function (m) {
        if (scrollPercent >= m && !reached[m]) {
          reached[m] = true;
          safeGtag('event', 'scroll_depth', {
            event_category: 'engagement',
            event_label: m + '%',
            percent: m,
            value: m,
          });
        }
      });
    } catch (e) {
      console.debug('scroll depth error', e);
    }
  }
  window.addEventListener(
    'scroll',
    function () {
      if (scrollTimeout) clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(trackScroll, 100);
    },
    { passive: true }
  );

  // ---- CTA & external links tracking & UTM append ----
  function appendUTM(url) {
    if (!url) return url;
    try {
      var u = new URL(url);
      if (!u.searchParams.get('utm_source')) {
        u.searchParams.set('utm_source', 'website');
        u.searchParams.set('utm_medium', 'organic');
        u.searchParams.set('utm_campaign', 'launch');
      }
      return u.toString();
    } catch (e) {
      return url; // leave it unchanged
    }
  }

  function addCTATracking() {
    const ctas = ['navCTA', 'heroCTA', 'pricingCTA', 'finalCTA', 'demoBtn'];
    ctas.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.addEventListener('click', function (e) {
          var text = (el.textContent || el.innerText || 'CTA').trim();
          safeGtag('event', 'cta_click', {
            event_category: 'conversion',
            event_label: text,
            value: 1,
          });
          // Hosted checkout links receive consistent conversion attribution.
          var href = el.getAttribute('data-href') || el.getAttribute('href');
          if (href && (href.includes('gumroad') || href.includes('gum.new') || href.includes('dodopayments.com'))) {
            e.preventDefault();
            safeGtag('event', 'checkout_intent', {
              event_category: 'conversion',
              event_label: text,
              value: 1,
            });
            var newHref = appendUTM(href);
            // Open in new tab to preserve behavior
            window.open(newHref, '_blank');
          }
        });
      }
    });
  }
  document.addEventListener('DOMContentLoaded', addCTATracking);

  // Also attach to existing anchor links which go to external sites
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[href^="http"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        const href = a.getAttribute('href');
        safeGtag('event', 'external_link_click', {
          event_category: 'navigation',
          event_label: href,
          link_text: (a.textContent || '').trim(),
        });
        if (href && (href.includes('gumroad') || href.includes('gum.new') || href.includes('dodopayments.com'))) {
          safeGtag('event', 'checkout_intent', {
            event_category: 'conversion',
            event_label: (a.textContent || '').trim() || href,
            value: 1,
          });
          a.href = appendUTM(href);
        }
      });
    });
  });

  // ---- Session Quality Scoring ----
  function computeQualityScore() {
    var score = 0;
    if (window.realUserDetected) score += 30;
    var timeOnPage = Math.floor((Date.now() - window.pageLoadTime) / 1000);
    if (timeOnPage > 5) score += 10;
    if (timeOnPage > 15) score += 10;
    if (timeOnPage > 30) score += 10;
    if (window.maxScroll > 25) score += 10;
    if (window.maxScroll > 50) score += 10;
    if (window.maxScroll > 75) score += 10;
    if (window.clickCount > 0) score += 10;
    return score;
  }

  var scoreReported = false;
  window.addEventListener('beforeunload', function () {
    if (!scoreReported) {
      scoreReported = true;
      var finalScore = computeQualityScore();
      safeGtag('event', 'session_quality', {
        event_category: 'engagement',
        value: finalScore,
        quality_tier:
          finalScore > 50 ? 'high' : finalScore > 20 ? 'medium' : 'low',
      });
    }
  });

  // Also send a checkpoint after 30 seconds
  setTimeout(function () {
    if (!scoreReported) {
      var score = computeQualityScore();
      if (score > 30)
        safeGtag('event', 'session_quality_checkpoint', {
          event_category: 'engagement',
          value: score,
        });
    }
  }, 30000);
})();
