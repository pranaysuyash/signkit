/*
 * Public checkout configuration for the static SignKit landing page.
 * Dodo product IDs are public identifiers, not secrets. Set the real SignKit
 * one-time product ID here after the product is active in Dodo Payments.
 */
window.SignKitCheckoutConfig = Object.freeze({
  dodoProductId: '',
  dodoBaseUrl: 'https://checkout.dodopayments.com/buy/',
  gumroadUrl: 'https://pranaysuyash.gumroad.com/l/signkit-v1',
});
