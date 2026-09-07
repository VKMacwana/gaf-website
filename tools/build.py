#!/usr/bin/env python3
"""Stitch shared header/footer around page bodies in tools/pages/*.html.

Usage: python3 tools/build.py   (writes final .html files to the repo root)
Page config lives in PAGES below; donate/action URLs in LINKS.
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "tools" / "pages"

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
    "india": ("india.html", "India — Guardian Angels Foundation",
              "Ongoing programs and initiatives across India, led by our Community Director, Mrs. Foram Christian.", "india"),
    "chicago-member-form": ("chicago-member-form.html", "Chicago-Midwest Chapter Membership Form — Guardian Angels Foundation",
                "Apply for membership with the Guardian Angels Foundation Chicago Midwest Chapter, or get in touch.", "chicago"),
}

NAV = [
    ("home", "/", "Home", None),
    ("programs", "/programs.html", "Programs", [
        ("chicago", "/chicago-midwest-chapter.html", "Chicago Chapter"),
        ("india", "/india.html", "India"),
    ]),
    ("about", "/about.html", "About", [
        ("involved", "/get-involved.html", "Get Involved"),
    ]),
    ("news", "/news.html", "News", None),
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
</script>
</body>
</html>
"""

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
            out.append(
                f'      <li class="{classes}">\n'
                f'        <a href="{href}">{label}</a>\n'
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
            HEAD.format(title=title, desc=desc, canonical=canonical, navlinks=navlinks(active))
            + body
            + FOOT
        )
        for key, val in LINKS.items():
            html = html.replace("{{" + key + "}}", val)
        leftover = re.findall(r"\{\{[A-Z_]+\}\}", html)
        if leftover:
            raise SystemExit(f"{slug}: unresolved placeholders {leftover}")
        (ROOT / outfile).write_text(html)
        print(f"built {outfile}")

if __name__ == "__main__":
    main()
