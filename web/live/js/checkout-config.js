/*
 * Public checkout configuration for the static SignKit landing page.
 * Dodo product IDs are public identifiers, not secrets. Set the real SignKit
 * one-time product ID here only after the product is active in Dodo Payments.
 * An empty or malformed Dodo ID intentionally makes Gumroad the primary
 * actionable provider. This object is the only public checkout configuration.
 */
window.SignKitCheckoutConfig = Object.freeze({
  dodoProductId: '',
  dodoBaseUrl: 'https://checkout.dodopayments.com/buy/',
  gumroadUrl: 'https://pranaysuyash.gumroad.com/l/signkit-v1',
});
