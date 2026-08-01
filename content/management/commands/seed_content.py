"""
Seed the database with the site's current hardcoded content so the frontend
looks identical once it switches to the API.

Usage:
    python manage.py seed_content            # skip project image downloads
    python manage.py seed_content --images   # also download gallery images
"""

import urllib.request
from datetime import date

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from content.models import (
    BlogPost,
    FooterSettings,
    Office,
    Project,
    ProjectImage,
    Service,
    SocialLink,
)

SERVICES = [
    {
        "slug": "brand-strategy",
        "what_we_define_heading": "What we define",
        "title": "Brand Strategy",
        "description": "Positioning, narrative, and identity architecture that gives your company a defensible point of view.",
        "tags": "Research, Positioning, Naming",
        "summary": "We clarify what you stand for, who you serve, and why the market should care — then turn that clarity into a system your team can actually run.",
        "what_we_define": "Category position, audience truths, competitive white space, brand narrative, naming options, and the messaging pillars that keep every launch coherent.",
        "how_we_work": "Workshops with founders and operators, market and competitor audits, narrative drafts, and a living strategy doc your marketing and product teams share.",
        "leave_with": "A sharp positioning statement\nNarrative and messaging framework\nNaming and verbal identity direction\nGo-forward brand principles",
    },
    {
        "slug": "visual-identity",
        "what_we_define_heading": "What we design",
        "title": "Visual Identity",
        "description": "Logo systems, typography, and motion built to scale across every surface your brand touches.",
        "tags": "Logo, Type, Motion",
        "summary": "Identity that holds up in a tab icon and on a stage screen — designed as a system, not a single logo file.",
        "what_we_define": "Logo and mark systems, type hierarchies, color logic, imagery direction, motion principles, and component rules for product and marketing.",
        "how_we_work": "Exploration from strategy, tight art direction rounds, production-ready files, and a lean brand guide your team can apply without us in the room.",
        "leave_with": "Primary and alternate logo lockups\nType, color, and layout system\nMotion and interaction language\nImplementation-ready assets",
    },
    {
        "slug": "product-and-web",
        "what_we_define_heading": "What we build",
        "title": "Product & Web",
        "description": "Marketing sites and product interfaces engineered with craft, clarity, and conversion at the core.",
        "tags": "Design, Build, Launch",
        "summary": "We design and ship the surfaces where your brand meets the customer — marketing sites, product UI, and the motion that makes them feel alive.",
        "what_we_define": "Marketing sites, landing systems, product interfaces, design systems, and front-end implementation with performance and accessibility baked in.",
        "how_we_work": "Structure and UX first, high-fidelity design, then production engineering — one team owning the handoff so nothing gets lost between Figma and ship.",
        "leave_with": "UX flows and information architecture\nHigh-craft UI and motion\nProduction front-end\nLaunch-ready QA and polish",
    },
    {
        "slug": "go-to-market",
        "what_we_define_heading": "What we plan",
        "title": "Go-to-Market",
        "description": "Launch strategy, messaging frameworks, and campaigns that compound attention into revenue.",
        "tags": "GTM, Campaigns, Content",
        "summary": "Launches that sound like your brand and convert like a machine — from narrative to creative to the cadence that keeps momentum after day one.",
        "what_we_define": "Launch narrative, channel strategy, campaign concepts, content systems, and the measurement loop that tells you what to double down on.",
        "how_we_work": "Tight collaboration with your growth and product leads, creative production as needed, and a playbook you can rerun for the next release.",
        "leave_with": "GTM narrative and messaging\nCampaign and content plan\nLaunch timeline and owners\nPost-launch learning loop",
    },
    {
        "slug": "content-systems",
        "what_we_define_heading": "What we build",
        "title": "Content Systems",
        "description": "Editorial voice, content models, and production rhythms that keep the brand sounding like itself.",
        "tags": "Voice, Editorial, Cadence",
        "summary": "A content engine your team can run — voice, formats, and a publishing system that compounds instead of starting from zero every week.",
        "what_we_define": "Brand voice and tone, content pillars, templates for key channels, and the editorial calendar logic that keeps output consistent.",
        "how_we_work": "Audit what you already publish, define the system with your marketing leads, then leave playbooks and examples your writers can extend.",
        "leave_with": "Voice and tone guidelines\nContent pillar framework\nChannel templates\nEditable publishing cadence",
    },
    {
        "slug": "design-systems",
        "what_we_define_heading": "What we deliver",
        "title": "Design Systems",
        "description": "Shared UI foundations so product and marketing ship faster without drifting apart.",
        "tags": "Components, Tokens, Docs",
        "summary": "Tokens, components, and documentation that keep every surface coherent — from marketing pages to the product your customers live in.",
        "what_we_define": "Design tokens, core components, usage rules, and a living library that engineering and design can both trust.",
        "how_we_work": "Inventory existing UI, define the smallest useful system, then implement and document so adoption is the default path.",
        "leave_with": "Token and type foundations\nCore component library\nUsage documentation\nHandoff-ready specs",
    },
    {
        "slug": "brand-audit",
        "what_we_define_heading": "What we assess",
        "title": "Brand Audit",
        "description": "A clear-eyed review of how your brand shows up — and where it leaks trust or attention.",
        "tags": "Audit, Gaps, Roadmap",
        "summary": "We map every major brand touchpoint, score what’s working, and hand you a prioritized roadmap — not a vague deck of opinions.",
        "what_we_define": "Identity consistency, messaging clarity, digital presence, campaign residue, and the operational habits that create drift.",
        "how_we_work": "Structured review across surfaces and stakeholders, then a findings workshop and a sequenced plan your team can act on.",
        "leave_with": "Touchpoint map and scores\nPriority gap analysis\nRecommended workstreams\n90-day action plan",
    },
    {
        "slug": "creative-direction",
        "what_we_define_heading": "What we lead",
        "title": "Creative Direction",
        "description": "Art direction for campaigns, films, and key moments when the brand has to look decisive.",
        "tags": "Art Direction, Campaigns, Film",
        "summary": "When the stakes are visible — a rebrand film, a flagship campaign, a launch moment — we set the creative bar and keep every frame on-brand.",
        "what_we_define": "Creative concepts, visual world-building, director and vendor briefing, and review cycles that protect the idea through production.",
        "how_we_work": "Tight concepting with your stakeholders, clear references and boards, then hands-on direction through finish.",
        "leave_with": "Creative platform and boards\nProduction brief package\nDirected review cycles\nFinal asset sign-off",
    },
]

# Legacy gallery tag → service slug mapping used only for seeding.
TAG_TO_SERVICE = {
    "WEBSITE": "product-and-web",
    "PRODUCT": "product-and-web",
    "PLATFORM": "product-and-web",
    "CAMPAIGN": "go-to-market",
    "SOCIAL": "go-to-market",
    "COMMUNICATION": "go-to-market",
    "CONTENT": "content-systems",
    "3D": "visual-identity",
    "MOTION": "visual-identity",
    "EXPERIENCE": "creative-direction",
    "PHYSICAL": "creative-direction",
    "EVENT": "creative-direction",
    "GAME": "creative-direction",
    "AI": "product-and-web",
    "VOICE": "product-and-web",
}

PROJECTS = [
    {"slug": "netflix-experience", "title": "NETFLIX", "subtitle": "STANGER THINGS EXPERIENCE", "tags": ["EXPERIENCE", "GAME", "PHYSICAL"], "year": 2025, "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=800&auto=format&fit=crop"},
    {"slug": "google-cloud", "title": "Google", "subtitle": "GOOGLE CLOUD BIGQUERY", "tags": ["COMMUNICATION", "SOCIAL", "CAMPAIGN"], "year": 2025, "image": "https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8?q=80&w=800&auto=format&fit=crop", "images": ["https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=1600&auto=format&fit=crop", "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1600&auto=format&fit=crop"]},
    {"slug": "zendesk-15", "title": "zendesk", "subtitle": "15 YEARS CAMPAIGN", "tags": ["EXPERIENCE", "WEBSITE", "CAMPAIGN"], "year": 2024, "image": "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?q=80&w=800&auto=format&fit=crop"},
    {"slug": "diageo-artistry", "title": "DIAGEO", "subtitle": "A BLEND OF ARTISTRY", "tags": ["EXPERIENCE", "3D", "AI"], "year": 2024, "image": "https://images.unsplash.com/photo-1504198453319-5ce911bafcde?q=80&w=800&auto=format&fit=crop"},
    {"slug": "doja-cat", "title": "DOJA CAT", "subtitle": "JUICY FRUIT CAMPAIGN", "tags": ["PRODUCT", "WEBSITE", "PLATFORM"], "year": 2024, "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=800&auto=format&fit=crop"},
    {"slug": "nike-run", "title": "NIKE", "subtitle": "AIR MAX FUTURE BEAT", "tags": ["EXPERIENCE", "PHYSICAL", "3D"], "year": 2025, "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=800&auto=format&fit=crop"},
    {"slug": "spotify-wrapped", "title": "Spotify", "subtitle": "WRAPPED INTERACTIVE", "tags": ["WEBSITE", "SOCIAL", "EXPERIENCE"], "year": 2024, "image": "https://images.unsplash.com/photo-1614680376593-902f74fa0d41?q=80&w=800&auto=format&fit=crop"},
    {"slug": "apple-vision", "title": "Apple", "subtitle": "VISION PRO SHOWCASE", "tags": ["EXPERIENCE", "3D", "PRODUCT"], "year": 2026, "image": "https://images.unsplash.com/photo-1608248597481-496100c8c836?q=80&w=800&auto=format&fit=crop"},
    {"slug": "judas-priest", "title": "JUDAS PRIEST", "subtitle": "SHIELD OF INDUSTRIAL MUSIC", "tags": ["EXPERIENCE", "WEBSITE", "SOCIAL"], "year": 2018, "image": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=800&auto=format&fit=crop"},
    {"slug": "google-voice", "title": "Google", "subtitle": "VOICE ASSISTANT IMMERSION", "tags": ["EXPERIENCE", "AI", "VOICE"], "year": 2025, "image": "https://images.unsplash.com/photo-1620121692029-d088224ddc74?q=80&w=800&auto=format&fit=crop"},
    {"slug": "netflix-games", "title": "NETFLIX", "subtitle": "ARCADE RETRO PARLOR", "tags": ["EXPERIENCE", "3D", "CONTENT"], "year": 2023, "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=800&auto=format&fit=crop"},
    {"slug": "diageo-whisky", "title": "DIAGEO", "subtitle": "SINGLE MALT JOURNEY", "tags": ["PRODUCT", "WEBSITE", "MOTION"], "year": 2024, "image": "https://images.unsplash.com/photo-1527061011665-3652c757a4d4?q=80&w=800&auto=format&fit=crop"},
    {"slug": "audi-rse", "title": "AUDI", "subtitle": "DRIVING EMOTION AR", "tags": ["3D", "EXPERIENCE", "GAME"], "year": 2025, "image": "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?q=80&w=800&auto=format&fit=crop"},
    {"slug": "sony-playstation", "title": "SONY", "subtitle": "PLAYSTATION 30TH ANNIVERSARY", "tags": ["WEBSITE", "CAMPAIGN", "SOCIAL"], "year": 2024, "image": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?q=80&w=800&auto=format&fit=crop"},
    {"slug": "balenciaga-cyber", "title": "BALENCIAGA", "subtitle": "CYBERPUNK METAVERSE RETAIL", "tags": ["EXPERIENCE", "PHYSICAL", "AI"], "year": 2026, "image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=800&auto=format&fit=crop"},
    {"slug": "redbull-stratos", "title": "RED BULL", "subtitle": "STRATOS INTERACTIVE MUSEUM", "tags": ["EXPERIENCE", "MOTION", "WEBSITE"], "year": 2023, "image": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?q=80&w=800&auto=format&fit=crop"},
    {"slug": "lego-build", "title": "LEGO", "subtitle": "CREATIVE BRICK BUILDER 3D", "tags": ["PRODUCT", "WEBSITE", "3D"], "year": 2025, "image": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?q=80&w=800&auto=format&fit=crop"},
    {"slug": "spotify-dj", "title": "Spotify", "subtitle": "AI DJ IMMERSIVE LAUNCH", "tags": ["AI", "CAMPAIGN", "EXPERIENCE"], "year": 2025, "image": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=800&auto=format&fit=crop"},
    {"slug": "prada-mode", "title": "PRADA", "subtitle": "PRADA MODE ARCHIVE", "tags": ["EXPERIENCE", "PHYSICAL", "EVENT"], "year": 2024, "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=800&auto=format&fit=crop"},
    {"slug": "tesla-optimus", "title": "TESLA", "subtitle": "OPTIMUS INTERFACE SUITE", "tags": ["PRODUCT", "AI", "WEBSITE"], "year": 2026, "image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800&auto=format&fit=crop"},
    {"slug": "gucci-vault", "title": "GUCCI", "subtitle": "GUCCI VAULT METAVERSE", "tags": ["EXPERIENCE", "3D", "WEBSITE"], "year": 2024, "image": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=800&auto=format&fit=crop"},
    {"slug": "louis-vuitton-voyage", "title": "LOUIS VUITTON", "subtitle": "TRAVEL TRUNK EXPLORER", "tags": ["EXPERIENCE", "MOTION", "PRODUCT"], "year": 2025, "image": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=800&auto=format&fit=crop"},
    {"slug": "ikea-place", "title": "IKEA", "subtitle": "PLACE AR SPATIAL RETAIL", "tags": ["PRODUCT", "WEBSITE", "3D"], "year": 2024, "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?q=80&w=800&auto=format&fit=crop"},
    {"slug": "space-x-starship", "title": "SPACEX", "subtitle": "STARSHIP FLIGHT SIMULATOR", "tags": ["EXPERIENCE", "3D", "PLATFORM"], "year": 2026, "image": "https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?q=80&w=800&auto=format&fit=crop"},
    {"slug": "hermes-dreams", "title": "HERMÈS", "subtitle": "KINETIC SCARF WINDOW", "tags": ["EXPERIENCE", "PHYSICAL", "MOTION"], "year": 2025, "image": "https://images.unsplash.com/photo-1479064555552-3ef4979f8908?q=80&w=800&auto=format&fit=crop"},
    {"slug": "ibm-quantum", "title": "IBM", "subtitle": "IBM QUANTUM COMPOSER", "tags": ["PLATFORM", "WEBSITE", "AI"], "year": 2025, "image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=800&auto=format&fit=crop"},
    {"slug": "samsung-flip", "title": "SAMSUNG", "subtitle": "GALAXY FLEX EXPERIENCE", "tags": ["PRODUCT", "WEBSITE", "MOTION"], "year": 2025, "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800&auto=format&fit=crop"},
    {"slug": "porsche-taycan", "title": "PORSCHE", "subtitle": "TAYCAN ELECTRIC PULSE", "tags": ["EXPERIENCE", "3D", "CAMPAIGN"], "year": 2024, "image": "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?q=80&w=800&auto=format&fit=crop"},
    {"slug": "netflix-onepiece", "title": "NETFLIX", "subtitle": "ONE PIECE AR CRUISE", "tags": ["WEBSITE", "SOCIAL", "3D"], "year": 2023, "image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=800&auto=format&fit=crop"},
    {"slug": "rtfkt-nike", "title": "RTFKT", "subtitle": "CLONEX CRYPTOKICKS", "tags": ["3D", "PRODUCT", "AI"], "year": 2024, "image": "https://images.unsplash.com/photo-1608248597481-496100c8c836?q=80&w=800&auto=format&fit=crop"},
    {"slug": "dior-ball", "title": "DIOR", "subtitle": "CHRISTIAN DIOR BALLROOM", "tags": ["EXPERIENCE", "PHYSICAL", "EVENT"], "year": 2025, "image": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?q=80&w=800&auto=format&fit=crop"},
    {"slug": "netflix-wednesday", "title": "NETFLIX", "subtitle": "WEDNESDAY SHADOW RUN", "tags": ["GAME", "WEBSITE", "CONTENT"], "year": 2023, "image": "https://images.unsplash.com/photo-1509248961158-e54f6934749c?q=80&w=800&auto=format&fit=crop"},
]

DEFAULT_PROJECT_DESCRIPTION = (
    "An immersive, state-of-the-art interactive campaign pushing the boundaries "
    "of technology and creativity to tell a compelling brand story."
)

DEFAULT_PROJECT_OVERVIEW = (
    "We partnered with the client to conceptualize, design, and engineer a unique "
    "digital ecosystem. By blending high-performance 3D animations, custom shader "
    "effects, and an intuitive user interface, we crafted an award-winning digital "
    "experience that drives massive engagement and positions them as pioneers in "
    "their field."
)

BLOGS = [
    {"slug": "brands-that-outlive-trends", "category": "Brand Strategy", "date": date(2026, 4, 18), "title": "Building brands that outlive trends", "subtitle": "Why the most durable companies invest in brand as infrastructure — not decoration.", "image_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=1600&auto=format&fit=crop", "read_time": "7 min read", "body": ["Trends are useful until they become a substitute for judgment. We see teams chase the look of the quarter — a typeface, a gradient, a motion language — and call the result a brand. Then the feed moves on, and so does the work.", "The companies that last treat brand as infrastructure: naming systems, voice, visual rules, and product patterns that survive a redesign cycle. Infrastructure is boring until you need it. Then it is the only thing that holds.", "When we start an engagement, we ask what must still be true in three years. Not what will photograph well next month. That question changes the brief, the deliverables, and how success gets measured.", "Decoration can be beautiful. Infrastructure compounds. Build for the second one."]},
    {"slug": "case-against-the-relaunch", "category": "Identity", "date": date(2026, 4, 2), "title": "The case against the relaunch", "subtitle": "Rebrands fail quietly. Here's how we've learned to tell the real ones from the cosmetic ones.", "image_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?q=80&w=1600&auto=format&fit=crop", "read_time": "6 min read", "body": ["A relaunch announces itself with a new logo and a press release. Six months later, the product still feels the same, support still writes the same way, and customers still describe the company with the old words. The rebrand happened on the surface. Nothing underneath moved.", "Real change is quieter. It shows up in how decisions get made, which work gets killed, and what the team refuses to ship. Identity is a set of constraints — not a campaign.", "We look for three signals before we commit to a full identity program: a shift in who the company serves, a shift in what it makes, or a shift in how it earns trust. Without one of those, a relaunch is costume.", "If the brief is “we need to look more premium,” pause. Ask what premium means in the product, the price, and the promise. Then design toward that — or don’t redesign at all."]},
    {"slug": "why-we-stopped-pitching", "category": "Studio", "date": date(2026, 3, 21), "title": "Why we stopped pitching", "subtitle": "Spec work is broken. We replaced it with a paid, two-week engagement. Here's what changed.", "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1600&auto=format&fit=crop", "read_time": "5 min read", "body": ["Pitch culture trains studios to guess. You get a thin brief, invent a strategy in a vacuum, and hope the room likes the slides. The client gets free thinking. You get a lottery ticket.", "We replaced open pitches with a paid, two-week diagnostic. Same intensity, clear scope, real access to stakeholders. At the end they own the work whether they continue with us or not.", "The quality jumped immediately. So did the honesty. When both sides are invested, bad ideas die faster and good ones get the airtime they need.", "We still compete. We just refuse to compete by giving the thinking away."]},
    {"slug": "systems-over-campaigns", "category": "Brand Strategy", "date": date(2026, 3, 8), "title": "Systems over campaigns", "subtitle": "Campaigns expire. Operating systems compound. How we brief work that still matters in two years.", "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=1600&auto=format&fit=crop", "read_time": "6 min read", "body": ["A campaign has a launch date and an end date. A system has rules that keep producing coherent work after the agency leaves the chat.", "We brief for systems: templates, tone ladders, component libraries, and decision trees. The “big idea” still matters — it just has to survive contact with next quarter’s product release.", "Teams that only buy campaigns stay dependent. Teams that buy systems get faster without getting sloppy."]},
    {"slug": "designing-for-silence", "category": "Product", "date": date(2026, 2, 24), "title": "Designing for silence", "subtitle": "The best interfaces feel invisible. Notes on restraint, pacing, and knowing when to stop.", "image_url": "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?q=80&w=1600&auto=format&fit=crop", "read_time": "5 min read", "body": ["Noise is easy to ship. Silence takes conviction. Every badge, tooltip, and celebratory animation asks for attention the user may not have.", "We design for the moment after the click — when nothing should happen except the thing the user intended. Motion earns its place by explaining, not decorating.", "If you can remove an element and the task still completes, remove it. Then remove one more."]},
    {"slug": "type-as-infrastructure", "category": "Identity", "date": date(2026, 2, 11), "title": "Type as infrastructure", "subtitle": "A type system is not a font pick. It is how a brand speaks under pressure across every surface.", "image_url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=1600&auto=format&fit=crop", "read_time": "6 min read", "body": ["Choosing a typeface is the smallest part of the job. The system is sizes, weights, line lengths, and the rules for when the voice gets loud or stays quiet.", "Under pressure — a crisis page, a dense dashboard, a three-word billboard — the type system either holds or fractures. We design for those moments first.", "If your brand only looks right in a hero poster, you do not have a type system. You have a mood board."]},
    {"slug": "motion-with-a-job", "category": "Motion", "date": date(2026, 1, 28), "title": "Motion with a job", "subtitle": "Animation that explains, not entertains. The rules we use before a single keyframe is drawn.", "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=1600&auto=format&fit=crop", "read_time": "5 min read", "body": ["Before we animate anything, we write the job: orient, confirm, warn, or delight. If we cannot name the job, we do not draw the timeline.", "Entertainment motion burns trust in product UI. Explanatory motion builds it. The difference is whether the user understands more after the movement ends.", "Reduced-motion paths are not an afterthought. They are the primary design, with motion as progressive enhancement."]},
    {"slug": "hiring-for-taste", "category": "Studio", "date": date(2026, 1, 14), "title": "Hiring for taste", "subtitle": "Portfolios lie. Craft shows up in the edits people refuse to ship. How we interview for that.", "image_url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=1600&auto=format&fit=crop", "read_time": "6 min read", "body": ["A polished case study can hide a weak process. We ask candidates to walk us through what they cut — and why. Taste lives in the delete key.", "We also watch how people talk about other people’s work. Generosity without standards is fluff. Standards without generosity is ego. We hire for both.", "Craft is not a vibe. It is a habit of attention under deadline."]},
    {"slug": "the-brief-is-the-product", "category": "Process", "date": date(2026, 1, 3), "title": "The brief is the product", "subtitle": "Most work fails before design starts. We treat the brief as a deliverable — not a formality.", "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=1600&auto=format&fit=crop", "read_time": "5 min read", "body": ["A vague brief produces confident-looking work that solves the wrong problem. We would rather spend a week sharpening the question than a month polishing the wrong answer.", "Our briefs name the audience, the job to be done, the constraints, and the definition of done. If any of those are missing, we are not ready to design.", "When the brief is clear, design gets faster — and critique gets kinder, because everyone is aiming at the same target."]},
]

OFFICES = [
    {"city": "Vietnam", "address": "Midtown, Phu My Hung, Ho Chi Minh City", "phone": "+84 91 9922034"},
    {"city": "China", "address": "193 Lockart Road, Hong Kong", "phone": "+86 186 16222144"},
    {"city": "Japan", "address": "6 Chome–6–2 Kojimachi, Tokyo", "phone": "+81 90 59480287"},
    {"city": "France", "address": "64–66 Rue des Archives, 75003 Paris, France", "phone": "+33 56 3264235"},
]

SOCIAL = [
    {"label": "Facebook", "url": "https://facebook.com"},
    {"label": "LinkedIn", "url": "https://linkedin.com"},
    {"label": "Instagram", "url": "https://instagram.com"},
]


class Command(BaseCommand):
    help = "Seed the database with the site's current content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--images",
            action="store_true",
            help="Download project gallery images into media storage.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Seeding services…")
        for i, data in enumerate(SERVICES):
            Service.objects.update_or_create(
                slug=data["slug"], defaults={**data, "order": i}
            )

        self.stdout.write("Seeding projects…")
        services_by_slug = {s.slug: s for s in Service.objects.all()}
        for i, data in enumerate(PROJECTS):
            project, _ = Project.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "order": i,
                    "title": data["title"],
                    "subtitle": data["subtitle"],
                    "description": DEFAULT_PROJECT_DESCRIPTION,
                    "overview": DEFAULT_PROJECT_OVERVIEW,
                    "date": date(data["year"], 1, 1),
                    "external_url": "",
                },
            )
            service_slugs = {
                TAG_TO_SERVICE[t] for t in data["tags"] if t in TAG_TO_SERVICE
            }
            project.services.set(
                [services_by_slug[s] for s in service_slugs if s in services_by_slug]
            )

            if options["images"] and not project.images.exists():
                urls = [data["image"], *data.get("images", [])]
                for j, url in enumerate(urls):
                    try:
                        with urllib.request.urlopen(url, timeout=20) as response:
                            content = response.read()
                        img = ProjectImage(project=project, order=j)
                        img.image.save(
                            f"{project.slug}-{j}.jpg", ContentFile(content), save=True
                        )
                        self.stdout.write(f"  ↳ {project.slug} image {j} ok")
                    except Exception as error:  # noqa: BLE001 — seed best-effort
                        self.stderr.write(f"  ↳ {project.slug} image {j} failed: {error}")

        self.stdout.write("Seeding blogs…")
        for data in BLOGS:
            body = "\n\n".join(data.pop("body"))
            BlogPost.objects.update_or_create(
                slug=data["slug"], defaults={**data, "description": body}
            )

        self.stdout.write("Seeding footer…")
        for i, data in enumerate(OFFICES):
            Office.objects.update_or_create(city=data["city"], defaults={**data, "order": i})
        for i, data in enumerate(SOCIAL):
            SocialLink.objects.update_or_create(
                label=data["label"], defaults={**data, "order": i}
            )
        FooterSettings.load()

        self.stdout.write(self.style.SUCCESS("Seed complete."))
