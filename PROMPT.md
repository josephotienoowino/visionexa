# Visionexa — Engineering Task Prompts

Prompts for evaluating an AI agent's ability to reason about and implement real features and fixes in this Flask portfolio application. Each prompt is grounded in actual observed behavior in the codebase. Models are expected to fall short on Turn 1. Keep it high level so the model has room to fail naturally.

---

## Task 1

**Task Type:** Feature Enhancement / Extension

**Gist:** The app stores skills and projects in a relational database but every public-facing page ignores that data entirely, showing hardcoded placeholder content instead — the admin CRUD is functionally decorative.

---

**Turn 1**

Something that keeps bothering me about the site: we went through the effort of building an admin panel where you can add skills, projects, all your portfolio work — but none of it shows up anywhere on the actual site that visitors see. If you go to the about page or the home page, you see these static cards that were just baked in during initial design, not anything that came from the database. So the admin CRUD is essentially decorative right now. A visitor looking at the site has no idea what projects I've done or what my skill set actually looks like, and that's the whole point of a portfolio.

What I'd expect is for the site to have at least one proper public-facing section — whether that's a dedicated portfolio/work page or integrated into the existing pages — that pulls from the real database records. Skills should show up with their levels displayed in some sensible way. Projects should show title, description, links where available, and dates if they're set. The layout should degrade gracefully when those fields are empty or not filled in. Adding or editing something in the admin should be immediately reflected on the site, no static content to manually sync.

There's also the question of ordering — projects and skills should come out in some predictable order, probably most recently added or manually sortable. Right now there's no way to control which projects get highlighted, and if the list grows, showing everything without any emphasis is going to look cluttered.

This should feel like a real portfolio section, not a JSON dump. The visual treatment matters. The existing site already has a design language — whatever gets built here needs to fit that, not look bolted on.

---

**What a senior engineer should have done:**

A senior engineer would have identified that the `Profile` model already carries `skills` and `projects` as SQLAlchemy relationships with cascade delete-orphan — meaning the data layer is done and correct. The work is entirely in the presentation and routing layers. They would have added a `/portfolio` or `/work` route under `main_bp` that queries the singleton profile via `Profile.query.first()` and passes its related skills and projects into a new template, with a graceful empty-state fallback if neither relation has rows. The about page's three hardcoded `<article>` "detail-card" elements — "Strategy-led work", "Human-centered design", "Reliable delivery" — would be identified as the placeholders they are and either replaced with data-driven content or removed entirely; they describe fictional work modes, not anything stored in the database. On the skills side, the `level` free-text field would be normalized into a display-safe format (stripped, title-cased) with a CSS width percentage or class mapped from the expected vocabulary (Beginner / Intermediate / Advanced / Expert), since the field has no enum enforcement. Project cards would conditionally render `url`, `github_url`, `image_url`, `start_date`, and `end_date` only when not None or empty, and fall back to a placeholder image when `image_url` is absent. A clear ordering strategy — newest by `id` DESC, or an explicit `display_order` integer column — would be chosen and documented, since the current models have no ordering field. The engineer would also observe that `Project.image_url` is never populated by the `add_project` API endpoint despite existing on the model, flag that as a separate bug requiring a decision, and not silently work around it.

---

## Task 2

**Task Type:** New Feature

**Gist:** Contact form submissions are fired off as emails and immediately forgotten — there is no database persistence, no admin inbox, and no way to recover a message if the SMTP server is down or misconfigured.

---

**Turn 1**

We have a contact form on the site and it's fine for the happy path — you fill it in, it sends me an email. But I realized recently that I have no idea how many people have actually tried to reach me through that form, because there's no record of any of it anywhere. If the mail server goes down, or the credentials expire, or someone submits on a day when the SMTP config is broken — that message is just gone. I have no fallback, no inbox, no audit trail.

Beyond the reliability problem there's a usability one: even when email delivery works fine, managing contact inquiries through a personal inbox mixed in with everything else is messy. I'd rather be able to open the admin panel and see a list of all the messages that have come in, mark them as read or reviewed, maybe note that I've handled it.

The current setup also has no safeguards. Someone could spam the form with hundreds of submissions and I'd either flood my inbox or — if email is broken — silently lose all of them. There's no real feedback to the person submitting either, just a flash message claiming it went through regardless of what actually happened.

What I want is a contact system that stores submissions persistently, gives me a place in the admin to manage them, and doesn't silently fail when email isn't configured. The email notification is nice-to-have but it shouldn't be the only thing standing between the user's message and oblivion. I also want some basic protection against abuse without it becoming a big engineering project.

---

**What a senior engineer should have done:**

A senior engineer would have added a `ContactMessage` model with fields for sender name, email, message body, `submitted_at` timestamp, and a boolean `is_read` flag — with no foreign key, since there is no user account system in this application. The contact POST route in `routes.py` currently calls `mail.send(msg)` inside the handler with no try/except and no database write; the fix is to write the `ContactMessage` row first, commit it, and only then attempt mail delivery in a try/except that logs failure and optionally sets a separate `email_delivered` boolean on the row — never surfacing the SMTP error to the submitter as a failure since the message is already safely stored. The admin blueprint would get a `/admin/contacts` list route showing all submissions sorted newest-first, with unread count surfaced in the dashboard stats cards that already exist, and a detail view that marks the message `is_read = True` when opened. For spam mitigation, a honeypot field — a hidden `<input>` that bots fill but humans leave blank — would be added to the contact form and checked in the POST handler; a submission with the honeypot populated gets silently discarded with a 200 response so the bot learns nothing. The engineer would also note that the form has no CSRF protection, that adding Flask-WTF is the correct fix for that, and would flag it explicitly rather than leaving it undocumented. A `__repr__` and `to_dict()` on the model would keep it consistent with how existing models in the codebase are structured.

---

## Task 3

**Task Type:** Feature Enhancement / Extension

**Gist:** The app already has a working file upload pipeline for learning content (PDFs, slide decks, documents), but profile photos and project images can only be set by pasting an external URL — the most visible parts of the site are entirely dependent on third-party image hosting.

---

**Turn 1**

I've been trying to update my profile photo and add proper images for a couple of project entries, and the experience is really awkward. The system expects me to paste in a URL — which means I have to upload the image somewhere else first, get a public link, and then come back and paste it. If that external host goes down or changes the URL, the image just breaks with no warning. It also means we're dependent on third-party hosting for some of the most visible parts of the site.

What's frustrating is that the site already knows how to handle file uploads. If I go into the learning content section and add a PDF or a slide deck, there's a proper file upload input, the file gets stored somewhere on the server, and it works. That mechanism exists. It just wasn't wired up for profile images or project images, which are honestly more important.

I'd like the admin forms for editing the profile and managing projects to support direct image uploads — choose a file, it gets stored, the right URL gets saved. The URL field could stay as a fallback if someone wants to link to an external image, but the primary flow should be uploading from disk. Reasonable file type restrictions and size limits should apply. When an image already exists for a record, the form should show what's currently set so you're not editing blind.

There's also the stale file problem — if I replace a project's image with a new one, the old file just sits on disk with nothing pointing to it. I don't want the uploads directory to quietly become a junk drawer over time.

---

**What a senior engineer should have done:**

A senior engineer would have recognized that `_save_file()` already exists in `routes.py` — it accepts a file object from `request.files`, validates the extension against `ALLOWED_EXTENSIONS`, generates a `uuid4`-prefixed safe filename via Werkzeug's `secure_filename`, and writes to `app/static/uploads/`. The gap is that this helper was only wired up for `Content` items and was never connected to the profile or project admin forms. The fix has two parts: extend `ALLOWED_EXTENSIONS` in `config.py` to include image types (`jpg`, `jpeg`, `png`, `gif`, `webp`) and create a dedicated `images/` subdirectory under `uploads/` for profile and project assets to keep them separate from PDF/document uploads. The admin `edit_profile` form would gain a file input for `profile_image`, and the POST handler would check `request.files.get('profile_image')` first — if present and valid, call `_save_file()` and store the returned path; fall back to the URL text field only if no file was submitted. The same pattern applies to the add and edit project forms. For stale file cleanup: before overwriting an existing image, check whether the current stored value starts with `/static/uploads/` (indicating it is a locally stored file, not an external URL); if so, call `os.remove()` on the old path wrapped in a `try/except` to handle already-missing files gracefully. The engineer would also note that `app/static/uploads/` should appear in `.gitignore` since user-uploaded binary files do not belong in version control, and flag that the current `add_project` API endpoint never reads `image_url` from the request body despite it existing on the model — that bug should be fixed in the same pass rather than left as a silent data gap.

---

## Task 4

**Task Type:** Debugging a tricky issue / Feature Enhancement / Extension

**Gist:** The learning portal has scheduling metadata and a published/draft toggle but enforces neither — scheduled sessions go live the moment you toggle them active, the whole content list loads at once with no pagination, and the date formatting code silently crashes on Windows.

---

**Turn 1**

The learn section is getting harder to manage as we add more content to it. A few things are broken or not working the way I intended them to.

The biggest one: when I schedule a live session for next week and mark it as active, it shows up on the portal immediately. The whole point of the scheduled datetime field was so that something could be staged in advance — a session I'm setting up shouldn't be browsable by learners until it's actually happening or at least close to it. Right now that datetime field is purely decorative, it just changes what the card displays, it doesn't affect whether the item shows up at all.

Related to that: I've had a few reports from people on Windows machines where certain content cards display incorrectly or cause page errors. I haven't been able to nail it down, but it seems tied to how dates get formatted somewhere in the page — not all content, specifically things that have a scheduled time set. It's not taking down the whole page but something is clearly wrong with how the scheduled time renders on those cards on Windows.

On the volume side, we're approaching sixty or seventy content items across all the courses and types. Right now the page loads all of them at once. That's already slow and it'll get worse. The filter tabs help but they're client-side once everything is loaded — we're still hitting the database for everything up front. We need some kind of server-side approach to keep this from getting unmanageable.

I want the scheduling to actually work — if something has a future scheduled time, don't show it yet. If it's a live session that's already ended, show it but mark it as past rather than showing a dead "Join session" button. And the date rendering needs to work correctly on every platform.

---

**What a senior engineer should have done:**

A senior engineer would have started with the Windows datetime crash: `learn/index.html` calls `.strftime('%A, %B %d at %-I:%M %p')` on `scheduled_at`, where `%-I` (no-padding 12-hour hour) is a Linux-only format directive that raises `ValueError` on Windows. The correct fix is to move all datetime formatting out of the Jinja2 template and into a Python function registered as a template filter via `app.jinja_env.filters['format_schedule']`; the function uses `%I` (zero-padded) and strips the leading zero with `lstrip('0')`, which is portable across platforms. Next, scheduling enforcement: the `/learn/` route currently queries `Content.query.filter_by(is_active=True)`; it should be extended to also require `(Content.scheduled_at == None) | (Content.scheduled_at <= datetime.utcnow())`, so future-dated items are withheld regardless of their active flag. Live sessions (`content_type == 'meet'`) with a `scheduled_at` that has already passed should be annotated in template context as ended and rendered with a "Session ended" state in place of the "Join session" CTA, since the existing button points to a dead meeting link. For pagination, the route would accept a `page` query param, use SQLAlchemy's `paginate(page=page, per_page=12)`, and pass the pagination object to the template; the filter tab links would carry both the active `type` and `course` params alongside `page=1` on tab change so filters and pagination compose correctly. The engineer would also flag that the existing client-side filter JavaScript becomes partially redundant once server-side filtering is in place — leaving both active creates inconsistent behavior — and would recommend converting the tabs to anchor links with query params rather than leaving contradictory UI logic silently in place.

---
