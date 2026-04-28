# Visionexa Task Prompts

This document contains task prompts designed to evaluate an AI agent's ability to identify gaps, reason about tradeoffs, and implement features in this Flask agency profile website. Each prompt is written from the perspective of a real engineer encountering a real problem, without naming specific files or methods.

---

## Task 1

**Task Type:** Feature Enhancement / Extension

**Gist:** The database stores a full portfolio — skills, projects with dates and links — but none of it renders anywhere on the website. Every visitor sees the same static placeholder content regardless of what's in the database.

**Turn 1**

I set up the database, added my skills and several projects with descriptions, links, and dates through the API, and then went to look at the site to see how it all comes together. Nothing shows up. Not the skills, not the projects, not a single piece of the portfolio data I've been building up. The about page just shows a block of bio text and some cards that I didn't write and can't change. The homepage shows the same generic blurb it always has.

The gap here is that the data layer and the presentation layer are completely disconnected. There's clearly a data model that was designed to hold a real portfolio — project titles, descriptions, URLs, GitHub links, dates, even images — but there's nowhere on the site where any of that data actually surfaces to a visitor. I'm supposed to be using this as a professional portfolio site, and right now I may as well not have a database at all.

I want the site to actually show what I've built. Projects should be displayed somewhere a visitor can find them — with enough information to understand what the work is and how to learn more. Skills should be visible too, ideally in a way that gives a sense of breadth and level rather than just a flat list. I'm not looking for a massive redesign, I just want the content I've put in to actually appear on the site in a coherent way.

**What a senior engineer should have done:**

The data model is fully built but completely disconnected from the HTML rendering layer. `Profile` has `skills` and `projects` relationships via SQLAlchemy backref — lazy-loaded, cascade delete-orphan — and `Project` has `title`, `description`, `url`, `github_url`, `image_url`, `start_date`, `end_date`. None of these fields are rendered anywhere in any template.

The `about` route in `routes.py` queries only `Profile.query.first()` and passes only `profile` to the template. The `about.html` template ignores `profile.skills` and `profile.projects` entirely and instead renders three hardcoded article elements ("Strategy-led work", "Human-centered design", "Reliable delivery") that have nothing to do with the database. The `view_profile` API endpoint does correctly query and serialize skills and projects — that logic can be referenced as the query pattern.

A senior engineer would update the `about` route (and likely add a `/work` or `/portfolio` route) to query skills and projects from the profile relationship, pass them to the template, and render them. Projects deserve a dedicated section: card layout with title, description, live link, GitHub link, and date range from `start_date`/`end_date`. Skills should render with their `level` field (Beginner/Intermediate/Advanced/Expert) as a visual indicator — not just a text label. The three hardcoded cards in `about.html` should either be removed or replaced with content from `content.yaml` to stay consistent with how the rest of the site handles static content. The engineer should also note that `image_url` on `Project` is stored but neither rendered in templates nor populated via the add endpoint — that inconsistency needs a decision: expose it or remove it.

---

## Task 2

**Task Type:** New Feature

**Gist:** The only way to update the profile, add skills, or manage projects is by sending raw JSON API requests from the command line. There is no browser-based interface for any content management — making the site impossible to maintain for anyone without developer tooling.

**Turn 1**

I've been managing this site by sending curl commands directly to the API whenever I want to update anything — change my bio, add a new skill, log a project I've finished. That was fine when I was building it, but now I'm trying to hand off basic maintenance to someone who isn't technical, and I'm realizing there's no way for them to actually do anything. The site has no management interface at all. Every write operation requires constructing a JSON payload and knowing the exact endpoint URL.

There's also no way to remove or edit things that already exist. I added a skill with a typo and there's no delete. I added a project description with the wrong date and there's no way to fix it short of rebuilding the database. The site is essentially append-only from a management perspective, and even the append path requires command-line access.

I need a way to manage this content from the browser. At minimum I want to be able to view and edit my profile, add and remove skills, and add, edit, and remove projects — without touching a terminal. I'm not worried about having multiple users or complex permissions. There's one owner of this site and they need to be able to run it without curl.

**What a senior engineer should have done:**

The write API has three POST-only endpoints in the `profile_bp` blueprint: `POST /profile/add` (upsert), `POST /profile/skill/add`, and `POST /profile/project/add`. There are zero DELETE or PUT endpoints. There is no authentication on any of these. There is no HTML form anywhere in the templates that targets these endpoints. The `Skill` and `Project` models both have `id` primary keys suitable for per-row operations, but no routes use them.

A senior engineer would recognize this is a single-owner site (the singleton `Profile.query.first()` pattern makes multi-user impossible) and build a simple `/admin` section rather than a full CMS. The minimum viable surface: a protected dashboard at `/admin` that shows the current profile and lets you edit it via an HTML form; a skills manager where you can see all skills and delete individual ones by ID; a projects manager with edit and delete per project. Protection should be a simple token or password check consistent with whatever auth approach was decided for the write API — not a full session system.

The engineer should also add the missing `DELETE /profile/skill/<id>` and `DELETE /profile/project/<id>` API endpoints, since a browser admin UI and a JSON API that both support delete is better than neither. They should note that the `add_skill` route currently has no deduplication guard — hitting "add" twice creates two identical rows — and the admin UI is the right place to surface and prevent that. All admin routes should be registered on a separate blueprint with a clear prefix, not mixed into `main_bp`.

---

## Task 3

**Task Type:** Feature Enhancement / Extension

**Gist:** The site has no SEO metadata, no Open Graph tags, and no per-page descriptions — every page looks identical to search engines and social media platforms, which is a significant gap for a design agency whose primary channel is inbound discovery.

**Turn 1**

I shared the site link in a few places and noticed that when it gets pasted into Slack, LinkedIn, or a text message, the preview is completely generic — just the domain name, no image, no description, nothing that communicates what the business does. I checked search results and the same problem shows up there: every page is indexed with the same title and no description snippet.

This is a serious problem for a design agency. The entire growth model depends on word-of-mouth and online discovery. When someone shares a link to the pricing page or the services page, the card preview that appears should tell them something useful — what Visionexa does, what the page is about, and ideally show a visual. Right now it shows nothing. The site is effectively invisible on social media regardless of how polished it looks when someone actually visits.

Beyond social sharing, there's no structure that tells search engines how to prioritize or understand the pages. Services, pricing, and contact are all treated identically in terms of metadata. I'd want each page to have a relevant description and title that fits the content on it, not a single fallback that covers every page the same way.

**What a senior engineer should have done:**

`base.html` contains `<meta charset="UTF-8">` and `<meta name="viewport">` — nothing else in the `<head>` beyond the font and CSS links. There is no `<meta name="description">`, no Open Graph block (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`), no Twitter card tags, and no canonical `<link>`. Every page's `{% block title %}` produces a single generic string with no per-page variation beyond the page name prefix.

A senior engineer would add a metadata block system to `base.html` using Jinja2 `{% block %}` tags: a `meta_description` block with a site-level default, and an `og_*` block set that each template can override. The implementation requires: a `{% block meta %}` in `<head>` that renders description, OG, and Twitter card tags using overridable block values; each page template sets a meaningful `meta_description` and `og_description` that reflects the actual page content; `og:image` points to a static asset (logo or default brand image) at minimum, with per-page override capability for project pages; `og:url` uses `request.url` to set the canonical URL dynamically.

The engineer should also note that `content.yaml` already has per-page headline and description strings for services, pricing, highlights, and commitments — those are the right source for `og:description` on each inner page rather than hardcoded strings in templates. The `contact.headline` and `contact.description` fields from YAML are passed to the contact template via context processor and should feed the contact page's meta description. This avoids duplicating copy between the visual content and the metadata.

---

## Task 4

**Task Type:** New Feature

**Gist:** Profile and project images are stored as plain URL strings in the database, but there is no way to actually upload an image through the site — leaving the homepage displaying a generic text placeholder where a professional photo should be, which undermines the credibility of a design agency.

**Turn 1**

The homepage has a big placeholder where my profile photo should be. It says "Visionexa Studio" in a box. I know the site stores an image URL in the database, but I've never been able to get an actual image to appear there because there's no way to upload one. I tried setting the URL to a path on the server, but that doesn't work because there's no upload endpoint — there's nowhere to actually send the file.

The same problem exists for projects. The data model clearly expects each project to have an image — probably a screenshot or mockup — but I've never been able to attach one to any project because, again, there's no upload mechanism. I've been pasting in external image URLs as a workaround, but I don't want to depend on third-party image hosts for a portfolio that's supposed to represent my work.

For a design studio, having a blank image slot on the homepage is embarrassing. Clients land there, see a gray rectangle, and the first impression of a studio that's supposed to be visually sophisticated is... a placeholder. I need to be able to upload images and have them show up on the site. I'm not trying to build an Instagram — just a profile photo and optionally a thumbnail per project.

**What a senior engineer should have done:**

`Profile.profile_image_url` and `Project.image_url` are both `db.Column(db.String(500))` — plain text fields that store a URL string. The `add_profile` route accepts `profile_image_url` via JSON but only stores whatever string is passed. The `add_project` route doesn't even read `image_url` from the request body — it's accepted by the model but never populated by the API. The homepage template renders `<img src="{{ profile.profile_image_url }}">` and falls back to a placeholder div if the field is empty.

A senior engineer would implement file upload using Flask's built-in `request.files` handling and Werkzeug's `secure_filename`. The upload surface needs: a `POST /admin/upload` endpoint that accepts a multipart form file, validates the extension (jpg, png, webp only), generates a unique filename using `uuid4`, saves to `app/static/uploads/`, and returns the relative URL; the `add_profile` and `add_project` routes updated to accept a file upload instead of or in addition to a URL string; an `uploads/` directory created and added to `.gitignore` (user uploads don't belong in version control).

The engineer should also set a file size limit — Flask's `MAX_CONTENT_LENGTH` config key — to prevent large uploads from buffering into memory. The `instance/` directory is not the right place for uploads since it's outside the static file serving path; `app/static/uploads/` is correct. They should handle the case where an existing profile image is replaced: the old file should be deleted from disk to prevent unbounded growth of the uploads directory. The `Project.image_url` field not being populated by `add_project` is a separate bug that should be fixed in the same pass.
