# Personal Portfolio

A polished, single-page personal website built with **Vite + React + TypeScript + Tailwind CSS**. Sticky nav with smooth scrolling and active-section highlighting, a hero, about, skills, an experience timeline, a projects grid, research, and a contact section — with scroll-reveal animations and full mobile responsiveness. Deploys free to GitHub Pages.

## Quick start

```bash
npm install
npm run dev      # local dev at http://localhost:5173
npm run build    # production build into /dist
npm run preview  # preview the production build
```

## Personalize it (this is the important part)

**Almost everything lives in one file: [`src/data/profile.ts`](src/data/profile.ts).** Open it and fill in:

- your name, tagline, location, hero blurb
- the About paragraphs and the quick-facts panel
- your social links (leave a field as `""` to hide that icon)
- `skills` — grouped into categories of tags
- `experience` — the timeline entries (most recent first)
- `projects` — the project grid cards
- `publications` — research / writing (delete the array's entries if you have none)

You don't need to touch any other source file to change content.

Then replace the placeholder assets in `public/`:

| File | What to do |
| --- | --- |
| `public/headshot.jpg` | Replace with a square photo of yourself (the "YN" circle is a placeholder). |
| `public/resume.pdf` | Drop in your actual resume — the Resume button links to it. |
| `public/favicon.svg` | Optional — change the initials or swap the icon. |

Also update the `<title>` and description tags in [`index.html`](index.html) so your name shows up in the browser tab and link previews.

## Re-theme in seconds

The whole site is driven by one accent color. Change the `forest` values in `tailwind.config.ts` (and the two `#14532d` references in `src/index.css` / `src/components/Contact.tsx`) to recolor everything. Fonts are set in `index.html` (Raleway) and `tailwind.config.ts`.

## Deploy to GitHub Pages

1. Create a new GitHub repo and push this code to the `main` branch.
2. In the repo, go to **Settings → Pages → Build and deployment**, and set **Source** to **GitHub Actions**.
3. Done. The included workflow (`.github/workflows/deploy.yml`) builds and deploys on every push to `main`.

### One base-path detail

- **Custom domain** or a repo named `your-username.github.io` → leave `base: "/"` in `vite.config.ts`.
- **Project repo** (served at `your-username.github.io/repo-name/`) → set `base: "/repo-name/"` in `vite.config.ts`.

### Custom domain (optional)

Add a file named `CNAME` in `public/` containing just your domain (e.g. `yourname.dev`), then point your domain's DNS at GitHub Pages per [GitHub's guide](https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site).

## Deploy elsewhere (Vercel / Netlify)

Both auto-detect Vite. Build command `npm run build`, output directory `dist`. Leave `base: "/"`.

## Project structure

```
src/
  data/profile.ts       ← edit this to change all content
  components/
    Nav.tsx             sticky nav + scroll-spy + mobile menu
    Hero.tsx            landing hero
    Section.tsx         reusable section wrapper (eyebrow + title + reveal)
    About.tsx  Skills.tsx  Experience.tsx  Projects.tsx  Research.tsx
    Contact.tsx  Footer.tsx  SocialLinks.tsx
  hooks/useReveal.ts    scroll-reveal (respects reduced-motion)
  lib/utils.ts          cn() classname helper
  App.tsx               composes the page
  index.css             global styles + animations
public/                 headshot, resume, favicon, robots.txt
```
