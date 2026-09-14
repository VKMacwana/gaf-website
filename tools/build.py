#!/usr/bin/env python3
"""Stitch shared header/footer around page bodies in tools/pages/*.html.

Usage: python3 tools/build.py   (writes final .html files to the repo root)
Page config lives in PAGES below; donate/action URLs in LINKS.
"""
import pathlib, re
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "tools" / "pages"
ASSETS_DIR = ROOT / "assets"

LINKS = {
    "GIVE_MAIN": "https://secure.myvanco.com/L-ZKFQ/home",
    "GIVE_KIT": "https://secure.myvanco.com/L-ZKFQ/campaign/C-14MXM",
    "GIVE_CHILD": "https://secure.myvanco.com/L-ZKFQ/campaign/C-14MXC",
    "GIVE_TREE": "https://secure.myvanco.com/L-ZKFQ/campaign/C-14QKR",
    "GIVE_REFUGEE_EMERGENCY": "https://secure.myvanco.com/L-ZKFQ/campaign/C-14MXB",
    "GIVE_STUDENT": "https://secure.myvanco.com/L-ZKFQ/home",
    "GIFT_BOOK": "https://secure.myvanco.com/L-ZKFQ/home",
    "PURCHASE_BOOK": "https://secure.myvanco.com/L-ZKFQ/campaign/C-14MXQ",
    "ANCHOR_POINT": "https://secure.myvanco.com/L-ZKFQ/campaign/C-16JA9",
    "ANCHOR_OTHERS": "https://secure.myvanco.com/L-ZKFQ/campaign/C-16JA8",
    "ANCHOR_FULL_SET": "https://secure.myvanco.com/L-ZKFQ/campaign/C-16JAA",
    "SPONSOR": "https://secure.myvanco.com/L-ZKFQ/home",
    "AWARD_FORM": "https://form.jotform.com/260275064438054",
    "GOFUNDME": "https://www.gofundme.com/charity/guardian-angels-foundation-inc/donate",
    "PAYPAL": "https://www.paypal.com/US/fundraiser/charity/5056846",
    "VENMO": "https://account.venmo.com/u/GuardianAngels-Foundation",
    "CRICKET": "https://www.americaplayscricket.org",
    "CRICKET_REGISTRATION": "https://secure.myvanco.com/L-ZKFQ/campaign/C-166W5",
    "SUPPORT_STUDENT": "https://secure.myvanco.com/L-ZKFQ/campaign/C-166W8",
    "ICSANA": "https://icsana.org/",
    "CHICAGO_DONATE": "https://secure.myvanco.com/L-ZKFQ/campaign/C-16JAH",
    "EMAIL": "help@guardianangels.foundation",
    "PHONE_TEL": "+12155563604",
    "PHONE_FMT": "+1 (215) 556-3604",
}

# slug -> (output file, <title>, meta description, active nav slug)
PAGES = {
    "index": ("index.html", "Guardian Angels Foundation — Inspire | Empower | Enrich",
              "Guardian Angels Foundation is a Christ-centered 501(c)(3) nonprofit advancing environmental stewardship, women's empowerment, and educational enrichment.", "home"),
    "about": ("about.html", "About & Mission — Guardian Angels Foundation",
              "Who we are, our mission, and our impact — a Christ-centered nonprofit guided by Psalm 91:11.", "about"),
    "programs": ("programs.html", "Our Programs — Guardian Angels Foundation",
                 "Healthy Woman Campaign, Sponsor-A-Child, tree planting, youth programs, crisis relief, and more.", "programs"),
    "student-empowerment": ("student-empowerment.html", "Student Empowerment Award — Guardian Angels Foundation",
                            "Recognizing students who use education to inspire, empower, and uplift others.", "programs"),
    "give": ("give.html", "Give — Guardian Angels Foundation",
             "Your donation is more than a gift — it's a lifeline. Give online, by PayPal, Zelle, GoFundMe, or check.", "give"),
    "sponsorship": ("sponsorship.html", "Corporate Sponsorship — Guardian Angels Foundation",
                    "Partner with Guardian Angels Foundation as a corporate sponsor and invest in your community.", "involved"),
    "get-involved": ("get-involved.html", "Get Involved — Guardian Angels Foundation",
                     "Volunteer, mentor, give, or spread the word — there's a place for you here.", "involved"),
    "volunteer": ("volunteer.html", "Volunteer — Guardian Angels Foundation",
                  "Help build a brighter tomorrow — apply to volunteer with Guardian Angels Foundation.", "involved"),
    "gift-shop": ("gift-shop.html", "Gift Shop — Guardian Angels Foundation",
                  "T-shirts and Gujarati translations of classic books — all proceeds support our charitable programs.", "involved"),
    "news": ("news.html", "News & Updates — Guardian Angels Foundation",
             "Latest news and updates from Guardian Angels Foundation.", "news"),
    "contact": ("contact.html", "Contact Us — Guardian Angels Foundation",
                "Get in touch with Guardian Angels Foundation — volunteer, donate, partner, or ask for help.", "contact"),
    "chicago-midwest-chapter": ("chicago-midwest-chapter.html", "Chicago-Midwest Chapter — Guardian Angels Foundation",
                "GAF Chicago Midwest Chapter — serving with compassion, empowering communities, and creating sustainable impact.", "chicago"),
    "give-chicago": ("give-chicago.html", "Give — Chicago-Midwest Chapter — Guardian Angels Foundation",
                "Support the GAF Chicago-Midwest Chapter by credit card, Venmo, Zelle, or check.", "chicago"),
    "india": ("india.html", "India — Guardian Angels Foundation",
              "Ongoing programs and initiatives across India, led by our Community Director, Mrs. Foram Christian.", "india"),
    "chicago-member-form": ("chicago-member-form.html", "Chicago-Midwest Chapter Membership Form — Guardian Angels Foundation",
                "Apply for membership with the Guardian Angels Foundation Chicago Midwest Chapter, or get in touch.", "chicago"),
    "america250": ("america250.html", "America250 Celebration — Guardian Angels Foundation",
                   "Guardian Angels Foundation celebrates America's Semiquincentennial — 250 years of the United States, 1776-2026.", "america250"),
    "canada-chapter": ("canada-chapter.html", "Canada Chapter — Guardian Angels Foundation",
                "GAF Canada Chapter — extending our mission of faith, compassion, and community service across Canada.", "canada"),
}

# Pages whose social-preview thumbnail should auto-follow whatever photo
# leads their list, rather than a fixed image (see first_item_image()).
OG_AUTO_SLUGS = {
    "news": "news-item",
    "india": "news-item",
}
# Fixed per-page thumbnails for pages excluded from the auto-follow above
# (e.g. because their first item's own photo is a text-heavy flyer that
# makes a poor link preview).
STATIC_OG_IMAGES = {
    "programs": "/assets/og-image-programs.jpg",
    "chicago-midwest-chapter": "/assets/og-image-chicago.jpg",
    "america250": "/assets/og-image-america250.jpg",
}
DEFAULT_OG_IMAGE = "/assets/og-image.jpg"

NAV = [
    ("home", "/", "Home", None),
    ("programs", None, "Programs", [
        ("programs", "/programs.html", "All Programs"),
        ("chicago", "/chicago-midwest-chapter.html", "Chicago Chapter"),
        ("america250", "/america250.html", "America250"),
    ]),
    ("about", None, "About", [
        ("about", "/about.html#mission", "Our Mission"),
        ("involved", "/get-involved.html", "Get Involved"),
    ]),
    ("news", None, "News", [
        ("news", "/news.html", "US Updates"),
        ("india", "/india.html", "India Updates"),
    ]),
    ("volunteer", "/volunteer.html", "Volunteer", None),
    ("contact", "/contact.html", "Contact", None),
]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.guardianangels.foundation/{canonical}">
<meta property="og:image" content="https://www.guardianangels.foundation{ogimage}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://www.guardianangels.foundation{ogimage}">
<link rel="canonical" href="https://www.guardianangels.foundation/{canonical}">
<link rel="icon" href="/assets/favicon-48.png" sizes="48x48">
<link rel="icon" href="/assets/favicon-512.png" sizes="512x512">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yantramanav:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header>
  <nav class="nav">
    <a class="nav-logo" href="/"><img src="/assets/logo-white.png" alt="Guardian Angels Foundation"></a>
    <button class="nav-toggle" aria-label="Menu" onclick="document.querySelector('.nav-links').classList.toggle('open')">&#9776;</button>
    <ul class="nav-links">
{navlinks}
      <li class="nav-social">
        <a href="https://www.facebook.com/GuardianAngelsFoundation1/" target="_blank" rel="noopener" aria-label="Guardian Angels Foundation on Facebook">
          <svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.78-3.89 1.1 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12"/></svg>
        </a>
        <a href="https://www.instagram.com/guardianangels.foundation/" target="_blank" rel="noopener" aria-label="Guardian Angels Foundation on Instagram">
          <svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M12 2c-2.72 0-3.06.01-4.12.06-1.06.05-1.79.22-2.43.47-.66.26-1.22.6-1.77 1.16a4.9 4.9 0 0 0-1.16 1.77c-.25.64-.42 1.37-.47 2.43C2 8.94 2 9.28 2 12s.01 3.06.06 4.12c.05 1.06.22 1.79.47 2.43.26.66.6 1.22 1.16 1.77.55.56 1.11.9 1.77 1.16.64.25 1.37.42 2.43.47C8.94 22 9.28 22 12 22s3.06-.01 4.12-.06c1.06-.05 1.79-.22 2.43-.47a4.9 4.9 0 0 0 1.77-1.16 4.9 4.9 0 0 0 1.16-1.77c.25-.64.42-1.37.47-2.43.05-1.06.06-1.4.06-4.12s-.01-3.06-.06-4.12c-.05-1.06-.22-1.79-.47-2.43a4.9 4.9 0 0 0-1.16-1.77 4.9 4.9 0 0 0-1.77-1.16c-.64-.25-1.37-.42-2.43-.47C15.06 2.01 14.72 2 12 2m0 1.8c2.67 0 2.99.01 4.04.06.98.04 1.5.21 1.86.35.47.18.8.4 1.15.75s.57.68.75 1.15c.14.36.31.88.35 1.86.05 1.05.06 1.37.06 4.04s-.01 2.99-.06 4.04c-.04.98-.21 1.5-.35 1.86-.18.47-.4.8-.75 1.15s-.68.57-1.15.75c-.36.14-.88.31-1.86.35-1.05.05-1.37.06-4.04.06s-2.99-.01-4.04-.06c-.98-.04-1.5-.21-1.86-.35a3.1 3.1 0 0 1-1.15-.75 3.1 3.1 0 0 1-.75-1.15c-.14-.36-.31-.88-.35-1.86C3.81 14.99 3.8 14.67 3.8 12s.01-2.99.06-4.04c.04-.98.21-1.5.35-1.86.18-.47.4-.8.75-1.15s.68-.57 1.15-.75c.36-.14.88-.31 1.86-.35C9.01 3.81 9.33 3.8 12 3.8m0 3.05a5.15 5.15 0 1 0 0 10.3 5.15 5.15 0 0 0 0-10.3m0 8.5a3.35 3.35 0 1 1 0-6.7 3.35 3.35 0 0 1 0 6.7m6.54-8.7a1.2 1.2 0 1 1-2.4 0 1.2 1.2 0 0 1 2.4 0"/></svg>
        </a>
        <a href="https://www.linkedin.com/company/guardian-angels-foundation-inc/" target="_blank" rel="noopener" aria-label="Guardian Angels Foundation on LinkedIn">
          <svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.03-1.85-3.03-1.86 0-2.14 1.45-2.14 2.94v5.66H9.36V9h3.41v1.56h.05c.48-.9 1.63-1.85 3.36-1.85 3.59 0 4.26 2.37 4.26 5.45zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12M7.12 20.45H3.56V9h3.56z"/></svg>
        </a>
      </li>
      <li><a class="btn btn-gold" href="/give.html">Donate</a></li>
    </ul>
  </nav>
</header>
<main>
"""

FOOT = """</main>
<footer>
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-logo">
        <img src="/assets/logo-footer-white.png" alt="Guardian Angels Foundation">
        <p>A Christ-centered 501(c)(3) nonprofit extending love and care to those in need &mdash; advancing environmental stewardship, empowering women, and enriching education.</p>
        <div class="footer-seals">
          <img src="/assets/seal-charitynav.png" alt="Charity Navigator">
          <img src="/assets/seal-candid.png" alt="Candid Bronze Seal of Transparency 2024">
          <img src="/assets/seal-candid-platinum.png" alt="Candid Platinum Seal of Transparency 2026">
        </div>
        <div class="footer-social">
          <a href="https://www.facebook.com/GuardianAngelsFoundation1/" target="_blank" rel="noopener" aria-label="Guardian Angels Foundation on Facebook">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.78-3.89 1.1 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12"/></svg>
          </a>
          <a href="https://www.instagram.com/guardianangels.foundation/" target="_blank" rel="noopener" aria-label="Guardian Angels Foundation on Instagram">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M12 2c-2.72 0-3.06.01-4.12.06-1.06.05-1.79.22-2.43.47-.66.26-1.22.6-1.77 1.16a4.9 4.9 0 0 0-1.16 1.77c-.25.64-.42 1.37-.47 2.43C2 8.94 2 9.28 2 12s.01 3.06.06 4.12c.05 1.06.22 1.79.47 2.43.26.66.6 1.22 1.16 1.77.55.56 1.11.9 1.77 1.16.64.25 1.37.42 2.43.47C8.94 22 9.28 22 12 22s3.06-.01 4.12-.06c1.06-.05 1.79-.22 2.43-.47a4.9 4.9 0 0 0 1.77-1.16 4.9 4.9 0 0 0 1.16-1.77c.25-.64.42-1.37.47-2.43.05-1.06.06-1.4.06-4.12s-.01-3.06-.06-4.12c-.05-1.06-.22-1.79-.47-2.43a4.9 4.9 0 0 0-1.16-1.77 4.9 4.9 0 0 0-1.77-1.16c-.64-.25-1.37-.42-2.43-.47C15.06 2.01 14.72 2 12 2m0 1.8c2.67 0 2.99.01 4.04.06.98.04 1.5.21 1.86.35.47.18.8.4 1.15.75s.57.68.75 1.15c.14.36.31.88.35 1.86.05 1.05.06 1.37.06 4.04s-.01 2.99-.06 4.04c-.04.98-.21 1.5-.35 1.86-.18.47-.4.8-.75 1.15s-.68.57-1.15.75c-.36.14-.88.31-1.86.35-1.05.05-1.37.06-4.04.06s-2.99-.01-4.04-.06c-.98-.04-1.5-.21-1.86-.35a3.1 3.1 0 0 1-1.15-.75 3.1 3.1 0 0 1-.75-1.15c-.14-.36-.31-.88-.35-1.86C3.81 14.99 3.8 14.67 3.8 12s.01-2.99.06-4.04c.04-.98.21-1.5.35-1.86.18-.47.4-.8.75-1.15s.68-.57 1.15-.75c.36-.14.88-.31 1.86-.35C9.01 3.81 9.33 3.8 12 3.8m0 3.05a5.15 5.15 0 1 0 0 10.3 5.15 5.15 0 0 0 0-10.3m0 8.5a3.35 3.35 0 1 1 0-6.7 3.35 3.35 0 0 1 0 6.7m6.54-8.7a1.2 1.2 0 1 1-2.4 0 1.2 1.2 0 0 1 2.4 0"/></svg>
          </a>
          <a href="https://www.linkedin.com/company/guardian-angels-foundation-inc/" target="_blank" rel="noopener" aria-label="Guardian Angels Foundation on LinkedIn">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.03-1.85-3.03-1.86 0-2.14 1.45-2.14 2.94v5.66H9.36V9h3.41v1.56h.05c.48-.9 1.63-1.85 3.36-1.85 3.59 0 4.26 2.37 4.26 5.45zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12M7.12 20.45H3.56V9h3.56z"/></svg>
          </a>
        </div>
      </div>
      <div>
        <h4>Explore</h4>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/about.html">About &amp; Mission</a></li>
          <li><a href="/programs.html">Our Programs</a></li>
          <li><a href="/news.html">News &amp; Updates</a></li>
          <li><a href="/contact.html">Contact Us</a></li>
        </ul>
      </div>
      <div>
        <h4>Get Involved</h4>
        <ul>
          <li><a href="/volunteer.html">Volunteer</a></li>
          <li><a href="/sponsorship.html">Corporate Sponsorship</a></li>
          <li><a href="/student-empowerment.html">Student Empowerment</a></li>
          <li><a href="/gift-shop.html">Gift Shop</a></li>
          <li><a href="/give.html">Give</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li>Morrisville, Pennsylvania, USA</li>
          <li><a href="tel:{{PHONE_TEL}}">{{PHONE_FMT}}</a></li>
          <li><a href="mailto:{{EMAIL}}">{{EMAIL}}</a></li>
        </ul>
        <p style="margin-top:14px"><a class="btn btn-gold" href="/give.html" style="padding:10px 22px;font-size:14px">Make a Donation</a></p>
      </div>
    </div>
  </div>
  <div class="footer-bottom">Copyright &copy; 2026 Guardian Angels Foundation &mdash; All Rights Reserved.</div>
</footer>
<script>
(function () {
  var slides = document.querySelectorAll('.hero-slides img');
  if (slides.length > 1) {
    var i = 0;
    setInterval(function () {
      slides[i].classList.remove('active');
      i = (i + 1) % slides.length;
      slides[i].classList.add('active');
    }, 6000);
  }
})();
(function () {
  document.querySelectorAll('.copy-link').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var url = location.origin + location.pathname + btn.dataset.hash;
      var flash = function (label) {
        var original = 'Copy Link';
        btn.textContent = label;
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = original;
          btn.classList.remove('copied');
        }, 1500);
      };
      var fallbackCopy = function () {
        var input = document.createElement('textarea');
        input.value = url;
        input.style.position = 'fixed';
        input.style.opacity = '0';
        document.body.appendChild(input);
        input.focus();
        input.select();
        try {
          document.execCommand('copy');
          flash('Copied!');
        } catch (e) {
          flash('Link: ' + url);
        }
        document.body.removeChild(input);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () {
          flash('Copied!');
        }, fallbackCopy);
      } else {
        fallbackCopy();
      }
    });
  });
})();
</script>
</body>
</html>
"""

def add_news_anchors(html):
    """Give every .news-item a stable #anchor id (derived from its date and
    title) plus a Copy Link button, so a single update can be shared
    directly instead of only linking to the whole news/india page."""
    used = set()

    def slugify(text):
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
        return text

    def repl(m):
        block = m.group(1)
        time_m = re.search(r"<time>(.*?)</time>", block, re.S)
        title_m = re.search(r"<h3>(.*?)</h3>", block, re.S)
        date_slug = slugify(time_m.group(1)) if time_m else ""
        title_text = re.sub(r"<[^>]+>", "", title_m.group(1)) if title_m else ""
        title_text = re.sub(r"&[a-zA-Z]+;", " ", title_text)
        words = re.findall(r"[A-Za-z0-9]+", title_text)[:6]
        title_slug = "-".join(w.lower() for w in words)
        base = "-".join(filter(None, [date_slug, title_slug])) or "update"
        anchor, n = base, 2
        while anchor in used:
            anchor = f"{base}-{n}"
            n += 1
        used.add(anchor)

        new_block = block.replace(
            "</time>",
            '</time>\n      <button class="copy-link" type="button" data-hash="#{0}">Copy Link</button>'.format(anchor),
            1,
        )
        return '<div class="news-item" id="{0}">\n{1}\n    </div>'.format(anchor, new_block)

    return re.sub(r'<div class="news-item">\n(.*?)\n {4}</div>', repl, html, flags=re.S)

def add_program_copy_links(html):
    """Add a Copy Link button after each program's title, reusing the
    program-row's existing id so one program can be shared directly."""
    def repl(m):
        row_id, block = m.group(1), m.group(2)
        new_block = re.sub(
            r"(<h3>.*?</h3>)",
            r'\1\n        <button class="copy-link" type="button" data-hash="#{0}">Copy Link</button>'.format(row_id),
            block,
            count=1,
            flags=re.S,
        )
        return m.group(0).replace(block, new_block)

    return re.sub(
        r'<div class="program-row[^"]*" id="([a-z0-9-]+)">\n(.*?)\n {4}</div>',
        repl,
        html,
        flags=re.S,
    )

def first_item_image(slug, item_class):
    """Return the image (or video poster) used by the first entry of a
    given item class ('news-item' or 'program-row') in a page's source,
    so the page's social-preview thumbnail can auto-follow whatever leads
    that list instead of a hand-picked photo that can go stale."""
    content = (PAGES_DIR / f"{slug}.html").read_text()
    blocks = re.findall(
        r'<div class="{0}[^"]*"[^>]*>\n(.*?)\n {{4}}</div>'.format(re.escape(item_class)),
        content, re.S,
    )
    if not blocks:
        return None
    img_m = re.search(r'<img src="([^"]+)"', blocks[0]) or re.search(r'poster="([^"]+)"', blocks[0])
    return img_m.group(1) if img_m else None

def make_og_image(src_rel, dst_rel, size=(1200, 630)):
    """Center-crop src_rel (an /assets/... path) to the social-preview
    aspect ratio and write it to dst_rel, so auto-selected photos never
    get awkwardly cropped by the platforms that render link previews."""
    src = ROOT / src_rel.lstrip("/")
    dst = ROOT / dst_rel.lstrip("/")
    im = Image.open(src).convert("RGB")
    target_ratio = size[0] / size[1]
    w, h = im.size
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        im = im.crop(((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h))
    else:
        new_h = int(w / target_ratio)
        im = im.crop((0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h))
    im = im.resize(size, Image.LANCZOS)
    im.save(dst, quality=88, optimize=True)

def og_image_for(slug):
    if slug in STATIC_OG_IMAGES:
        return STATIC_OG_IMAGES[slug]
    item_class = OG_AUTO_SLUGS.get(slug)
    if not item_class:
        return DEFAULT_OG_IMAGE
    src = first_item_image(slug, item_class)
    if not src:
        return DEFAULT_OG_IMAGE
    dst = f"/assets/og-image-{slug}.jpg"
    make_og_image(src, dst)
    return dst

def recent_activity(slug, href, n=3):
    """Pull the first n .news-item entries out of a page's source fragment
    (entries are already kept newest-first) and render them as card tiles
    (image + date + title) matching the site's grid-3 card style."""
    content = (PAGES_DIR / f"{slug}.html").read_text()
    blocks = re.findall(r'<div class="news-item">\n(.*?)\n {4}</div>', content, re.S)
    cards = []
    for block in blocks[:n]:
        time_m = re.search(r"<time>(.*?)</time>", block, re.S)
        title_m = re.search(r"<h3>(.*?)</h3>", block, re.S)
        if not time_m or not title_m:
            continue
        date = time_m.group(1).strip()
        title = re.sub(r"\s+", " ", title_m.group(1)).strip()
        # strip any nested links (e.g. inline "See full gallery" CTAs) since the
        # whole card is already a link and nested <a> tags are invalid HTML
        title = re.sub(r"<a[^>]*>(.*?)</a>", r"\1", title, flags=re.S).strip()
        img_m = re.search(r'<img src="([^"]+)"', block) or re.search(r'poster="([^"]+)"', block)
        thumb = img_m.group(1) if img_m else "/assets/icon-heart.png"
        cards.append(
            '      <a class="card recent-card" href="{href}">\n'
            '        <img class="card-img" src="{thumb}" alt="">\n'
            '        <div class="card-body">\n'
            '          <h3>{title}</h3>\n'
            '          <time>{date}</time>\n'
            '        </div>\n'
            '      </a>'.format(href=href, thumb=thumb, date=date, title=title)
        )
    return "\n".join(cards)

def navlinks(active):
    out = []
    for slug, href, label, children in NAV:
        if children:
            child_slugs = [c[0] for c in children]
            section_active = active == slug or active in child_slugs
            classes = "nav-item has-dropdown" + (" current-section" if section_active else "")
            child_items = []
            for cslug, chref, clabel in children:
                ccur = ' aria-current="page"' if active == cslug else ""
                child_items.append(f'          <li><a href="{chref}"{ccur}>{clabel}</a></li>')
            child_html = "\n".join(child_items)
            trigger = f'<a href="{href}">{label}</a>' if href else f'<span class="nav-trigger">{label}</span>'
            out.append(
                f'      <li class="{classes}">\n'
                f'        {trigger}\n'
                f'        <ul class="nav-dropdown">\n'
                f'{child_html}\n'
                f'        </ul>\n'
                f'      </li>'
            )
        else:
            cur = ' aria-current="page"' if slug == active else ""
            out.append(f'      <li><a href="{href}"{cur}>{label}</a></li>')
    return "\n".join(out)

def main():
    for slug, (outfile, title, desc, active) in PAGES.items():
        body = (PAGES_DIR / f"{slug}.html").read_text()
        canonical = "" if outfile == "index.html" else outfile
        html = (
            HEAD.format(title=title, desc=desc, canonical=canonical, navlinks=navlinks(active),
                        ogimage=og_image_for(slug))
            + body
            + FOOT
        )
        for key, val in LINKS.items():
            html = html.replace("{{" + key + "}}", val)
        if "{{RECENT_US}}" in html:
            html = html.replace("{{RECENT_US}}", recent_activity("news", "/news.html"))
        if "{{RECENT_INDIA}}" in html:
            html = html.replace("{{RECENT_INDIA}}", recent_activity("india", "/india.html"))
        html = add_news_anchors(html)
        html = add_program_copy_links(html)
        leftover = re.findall(r"\{\{[A-Z_]+\}\}", html)
        if leftover:
            raise SystemExit(f"{slug}: unresolved placeholders {leftover}")
        (ROOT / outfile).write_text(html)
        print(f"built {outfile}")

if __name__ == "__main__":
    main()
