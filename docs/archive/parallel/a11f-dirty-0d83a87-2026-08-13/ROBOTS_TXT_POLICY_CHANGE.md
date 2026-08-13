# Robots.txt Policy Change - AI Search Era SEO

## Date
November 26, 2025

## Summary
Updated robots.txt from blocking AI crawlers to allowing AI search indexing while maintaining protection against training data scraping.

## Previous Configuration

### What We Had
```
User-agent: *
Allow: /

Sitemap: https://signkit.work/sitemap.xml

Disallow: /admin/
Disallow: /.git/
Disallow: /node_modules/

Allow: /assets/
Allow: /css/
Allow: /js/
Allow: /images/

Crawl-delay: 1
```

### Why We Had It
- Simple, permissive configuration
- Allowed all search engines
- Basic protection for internal paths
- No specific AI crawler policies

### Problems with Previous Config
- No explicit AI crawler policy
- Cloudflare had added restrictive AI bot blocks (Amazonbot, ClaudeBot, GPTBot, etc.)
- Prevented SignKit from appearing in AI-powered search results
- Blocked the very tools (ChatGPT, Perplexity, Claude) that users now use for product discovery
- Counterproductive for a landing page that needs maximum SEO visibility

## New Configuration

### What We Changed To
```
# robots.txt for signkit.work - AI Search Era SEO Policy

User-agent: *
Content-signal: search=yes,ai-input=yes,ai-train=no
Allow: /

# Sitemaps
Sitemap: https://signkit.work/sitemap.xml

# Disallow admin/internal paths
Disallow: /admin/
Disallow: /.git/
Disallow: /node_modules/

# Allow all assets
Allow: /assets/
Allow: /css/
Allow: /js/
Allow: /images/

# Crawl-delay (optional, helps with server load)
Crawl-delay: 1
```

### Why We Changed

#### Business Context
- SignKit is a product landing page focused on SEO and discovery
- Users increasingly find products through AI chat interfaces (ChatGPT, Perplexity, Claude, etc.)
- Being cited in AI search results drives qualified traffic
- Landing pages need maximum visibility in modern search landscape

#### Technical Reasoning
**Content Signals Explained:**
- `search=yes` - Allow traditional search indexing (Google, Bing, etc.)
- `ai-input=yes` - Allow real-time AI search with attribution (RAG/retrieval augmented generation)
- `ai-train=no` - Block wholesale training data scraping

**Key Differences:**
- **AI Training**: Takes your content permanently into model weights, no attribution, no traffic back
- **AI Search/Input**: References your content with citations, drives traffic to your site
- **Traditional Search**: Indexes and links back to you

#### Benefits of New Policy
✅ Show up in ChatGPT search results when users ask about signature tools  
✅ Get cited by Perplexity, Claude, and other AI search engines  
✅ Drive qualified traffic from AI-powered product discovery  
✅ Maintain protection against training data scraping  
✅ Support the AI tools we ourselves use and value  
✅ Align with modern SEO best practices for 2025  

#### What We're Protecting Against
❌ Wholesale scraping for model training (GPT-5, Claude 4, etc.)  
❌ Content being absorbed into models without attribution  
❌ Commercial use of our content in training datasets  

#### What We're Enabling
✅ Real-time AI search that cites sources  
✅ AI assistants that link back to our site  
✅ Product discovery through conversational AI  
✅ Modern search engine visibility  

## Implementation

### Files Changed
- `web/live/robots.txt` (on landing-page branch)

### Deployment
1. Updated on landing-page branch
2. Deployed to Cloudflare Pages
3. Effective immediately at https://signkit.work/robots.txt

### Verification
Check live policy:
```bash
curl https://signkit.work/robots.txt
```

## References

### Content Signal Standard
Based on emerging web standards for AI crawler policies:
- `search` - Traditional search indexing
- `ai-input` - Real-time AI search/RAG
- `ai-train` - Model training data collection

### EU Copyright Directive
Content signals reference Article 4 of EU Directive 2019/790 on copyright and related rights in the Digital Single Market.

## Decision Rationale

This change reflects the reality that:
1. We use LLMs ourselves and value AI assistance
2. Our landing page exists to be discovered
3. AI search is now a primary discovery channel
4. Blocking AI search tools was counterproductive to our SEO goals
5. We can allow AI search while still protecting against training scraping

The irony of blocking AI tools while using them ourselves was the catalyst for this policy review.

## Future Considerations

- Monitor AI search referral traffic in analytics
- Track citations in AI search results
- Adjust policy if training vs. search distinction changes
- Consider more granular bot-specific policies if needed

---

**Status**: Implemented  
**Branch**: landing-page  
**Deployed**: Cloudflare Pages  
**Effective**: November 26, 2025
