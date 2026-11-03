// The site map, in one place: the header menus, the footer columns and the link lists on the 404
// and thank-you pages read from here. Added Nov 2, 2026 when the founder asked for the sections
// Vanta and Drata have and we did not (solutions, integrations, frameworks, customers, help,
// academy, community, press, careers, security, trust, status, legal) "even if there's no content
// for now". Pages that are placeholders say so on the page itself, never here.
import { brand, decided, framework, frameworkHref } from "./config.js";

const demo = decided(brand.demo_url);

/** A framework's guide page link, from its catalog id. */
const guide = (id) => ({ href: frameworkHref(id), label: framework(id).short });

/** Header menus. A top-level entry with `groups` is a dropdown; one without is a plain link. `icon` names a
 * drawing in icons.js; the header shows it above the label, as the product's menu strip does (Nov 3, 2026). */
export const MENUS = [
  {
    label: "Platform",
    icon: "platform",
    href: "/platform",
    groups: [
      {
        title: "The platform",
        items: [
          { href: "/platform", label: "Overview", text: "Connect, watch, fix, prove" },
          { href: "/integrations", label: "Integrations", text: "Read-only connections, what each one reads" },
          { href: "/frameworks", label: "Frameworks", text: "The catalog, grouped by who asks" },
          { href: "/security", label: "Security", text: "How the platform protects your data" },
          ...(demo ? [{ href: demo, label: "See the product", text: "A sample company, no sign-up", external: true }] : []),
        ],
      },
      {
        title: "Modules",
        items: [
          { href: "/platform#controls", label: "Controls and monitoring" },
          { href: "/platform#evidence", label: "Evidence" },
          { href: "/platform#policies", label: "Policies" },
          { href: "/platform#people", label: "People and training" },
          { href: "/platform#vendors", label: "Vendors and risks" },
          { href: "/platform#ai", label: "AI governance" },
          { href: "/platform#trust", label: "Trust page and questionnaires" },
          { href: "/platform#assistant", label: "The assistant" },
        ],
      },
    ],
  },
  {
    label: "Solutions",
    icon: "solutions",
    href: "/solutions",
    groups: [
      {
        title: "By who sent you",
        items: [
          { href: "/solutions#broker", label: "Your insurance broker" },
          { href: "/solutions#accountant", label: "Your accountant" },
          { href: "/solutions#customer", label: "A customer or your attorney" },
          { href: "/solutions#provider", label: "Your IT provider" },
        ],
      },
      {
        title: "By industry",
        items: [
          { href: "/solutions#healthcare", label: "Healthcare" },
          { href: "/solutions#financial", label: "Financial services and insurance" },
          { href: "/solutions#software", label: "Software and IT services" },
          { href: "/solutions#professional", label: "Professional services" },
          { href: "/solutions#public", label: "Government suppliers" },
          { href: "/solutions#manufacturing", label: "Manufacturing and logistics" },
        ],
      },
      {
        title: "By size",
        items: [
          { href: "/solutions#size", label: "10 to 25 people" },
          { href: "/solutions#size", label: "25 to 100 people" },
          { href: "/solutions#size", label: "100 to 500 people" },
          { href: "/solutions#size", label: "500 people and more" },
        ],
      },
    ],
  },
  { label: "Frameworks", icon: "frameworks", href: "/frameworks" },
  { label: "Pricing", icon: "pricing", href: "/pricing" },
  { label: "Compare", icon: "compare", href: "/compare" },
  {
    label: "Partners",
    icon: "partners",
    href: "/for-partners",
    groups: [
      {
        title: "Work with Alimi",
        items: [
          { href: "/for-partners", label: "For partners", text: "Refer or resell; the terms are published" },
          { href: "/for-resellers", label: "For resellers", text: "Wholesale tiers, incentives, white label" },
          { href: "/for-partners#referrers", label: "For referrers", text: "Brokers, CPAs and attorneys" },
          { href: "/for-partners#partner-form", label: "Become a partner", text: "A short form and a 30-minute call" },
        ],
      },
    ],
  },
  {
    label: "Resources",
    icon: "resources",
    href: "/resources",
    wide: true,
    groups: [
      {
        title: "Customers",
        items: [
          { href: "/customers", label: "Customer stories", text: "Hear from the companies that run on Alimi" },
          { href: "/help", label: "Help center", text: "Find the help you need to get started" },
          { href: "/academy", label: "Alimi Academy", text: "Deepen your security knowledge and learn new skills" },
          { href: "/community", label: "Alimi Community", text: "Connect with other Alimi users" },
          { href: "/pricing#services", label: "Instructor-led training", text: "Live workshops for your finance team and your staff" },
        ],
      },
      {
        title: "Company",
        items: [
          { href: "/about", label: "About", text: "Learn more about Alimi" },
          { href: "/security", label: "Security", text: "How Alimi secures its own platform" },
          { href: "/press", label: "Press", text: "News, boilerplate and the media contact" },
          { href: "/careers", label: "Careers", text: "Who joins, and when" },
        ],
      },
      {
        title: "Compliance resources",
        items: [
          guide("soc2"),
          guide("iso27001"),
          guide("hipaa"),
          guide("iso42001"),
          guide("gdpr"),
          guide("pci_dss"),
          guide("cyber_essentials"),
          guide("hitrust"),
          guide("cmmc"),
          guide("fedramp"),
          { href: "/platform#vendors", label: "TPRM" },
          { href: "/platform#trust", label: "Trust" },
          { href: "/platform", label: "GRC" },
        ],
      },
      {
        title: "All resources",
        items: [
          { href: "/resources", label: "Resource library", text: "Guides, glossary, templates, webinars" },
          { href: "/frameworks", label: "Framework guides", text: "One page per framework" },
          { href: "/glossary", label: "Glossary", text: "Every term, in plain English" },
          { href: "/resources#webinars", label: "Webinars and events" },
          { href: "/resources#blog", label: "Blog" },
        ],
      },
    ],
  },
  { label: "Contact", icon: "contact", href: "/contact", button: true },
];

/** Footer columns. */
export const FOOTER = [
  {
    title: "Platform",
    items: [
      { href: "/platform", label: "Overview" },
      { href: "/integrations", label: "Integrations" },
      { href: "/frameworks", label: "Frameworks" },
      { href: "/security", label: "Security" },
      { href: "/pricing", label: "Pricing" },
      { href: "/pricing#services", label: "Services" },
      { href: "/compare", label: "Compare with Vanta and Drata" },
      ...(demo ? [{ href: demo, label: "See the product", external: true }] : []),
    ],
  },
  {
    title: "Solutions",
    items: [
      { href: "/solutions#sender", label: "By who sent you" },
      { href: "/solutions#industry", label: "By industry" },
      { href: "/solutions#size", label: "By company size" },
      { href: "/solutions#frameworks", label: "By framework" },
    ],
  },
  {
    title: "Resources",
    items: [
      { href: "/resources", label: "Resource library" },
      { href: "/frameworks", label: "Framework guides" },
      { href: "/glossary", label: "Glossary" },
      { href: "/customers", label: "Customer stories" },
      { href: "/help", label: "Help center" },
      { href: "/academy", label: "Alimi Academy" },
      { href: "/community", label: "Community" },
    ],
  },
  {
    title: "Partners",
    items: [
      { href: "/for-partners", label: "For partners" },
      { href: "/for-resellers", label: "For resellers" },
      { href: "/for-partners#referrers", label: "For referrers" },
      { href: "/for-partners#partner-form", label: "Become a partner" },
    ],
  },
  {
    title: "Company",
    items: [
      { href: "/about", label: "About" },
      { href: "/press", label: "Press" },
      { href: "/careers", label: "Careers" },
      { href: "/trust", label: "Trust page" },
      { href: "/status", label: "Status" },
      { href: "/legal", label: "Legal and privacy" },
      { href: "/contact", label: "Contact" },
    ],
  },
];

/** The short list of main pages, for the 404 and thank-you pages. */
export const MAIN_PAGES = [
  { href: "/platform", label: "The platform" },
  { href: "/frameworks", label: "Frameworks" },
  { href: "/solutions", label: "Solutions" },
  { href: "/pricing", label: "Pricing" },
  { href: "/compare", label: "Compare" },
  { href: "/for-partners", label: "For partners" },
  { href: "/resources", label: "Resources" },
  { href: "/about", label: "About" },
];

/** Every internal path the site map points at, without fragments, for the build check. */
export function siteMapPaths() {
  const out = new Set();
  const add = (href) => {
    if (typeof href !== "string" || !href.startsWith("/")) return;
    out.add(href.split("#")[0]);
  };
  for (const menu of MENUS) {
    add(menu.href);
    for (const group of menu.groups ?? []) for (const item of group.items) add(item.href);
  }
  for (const column of FOOTER) for (const item of column.items) add(item.href);
  for (const page of MAIN_PAGES) add(page.href);
  return [...out].sort();
}

/**
 * The breadcrumb trail for a page, for the light bar under the header: Home, then the top-level menu
 * that lists the page (if any), then the page itself. Derived from the menus, so no page spells it out.
 */
export function breadcrumbs(path, title) {
  const clean = (href) => href.split("#")[0];
  const trail = [{ href: "/", label: "Home" }];
  if (path === "/") return trail;
  // A page under a menu's own path (a framework page under /frameworks) belongs to that menu, even when
  // another menu also links to it, so the trail agrees with the highlighted item in the strip.
  const menu =
    MENUS.find((m) => clean(m.href) === path) ??
    MENUS.find((m) => clean(m.href) !== "/" && path.startsWith(`${clean(m.href)}/`)) ??
    MENUS.find((m) => (m.groups ?? []).some((g) => g.items.some((i) => !i.external && clean(i.href) === path)));
  if (menu && clean(menu.href) !== path) trail.push({ href: clean(menu.href), label: menu.label });
  trail.push({ href: path, label: title, current: true });
  return trail;
}
