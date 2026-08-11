import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { profile } from "@/data/profile";

const links = [
  { id: "about", label: "About" },
  { id: "skills", label: "Skills" },
  { id: "experience", label: "Experience" },
  { id: "projects", label: "Projects" },
  { id: "education", label: "Education" },
  { id: "awards", label: "Awards" },
  { id: "contact", label: "Contact" },
];

const Nav = () => {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState<string>("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const sections = links
      .map((l) => document.getElementById(l.id))
      .filter(Boolean) as HTMLElement[];

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach((s) => observer.observe(s));
    return () => observer.disconnect();
  }, []);

  const go = (id: string) => {
    setOpen(false);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <header
      className={cn(
        "fixed top-0 inset-x-0 z-50 transition-all duration-300",
        scrolled
          ? "bg-white/80 backdrop-blur-md border-b border-neutral-200"
          : "bg-transparent"
      )}
    >
      <div className="max-w-5xl mx-auto px-6 sm:px-8 h-16 flex items-center justify-between">
        {/* Mark */}
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="flex items-center gap-2 group"
          aria-label="Back to top"
        >
          <span className="w-8 h-8 rounded-md bg-brand-gradient text-white grid place-items-center text-[13px] font-bold tracking-tight">
            {profile.navMark}
          </span>
          <span className="text-[15px] font-semibold text-forest-dark hidden lg:inline">
            {profile.name}
          </span>
        </button>

        {/* Desktop links */}
        <nav className="hidden md:flex items-center gap-5 lg:gap-6 text-[13.5px]">
          {links.map((l) => (
            <button
              key={l.id}
              onClick={() => go(l.id)}
              className={cn(
                "transition-colors duration-200 relative",
                active === l.id
                  ? "text-forest-dark"
                  : "text-neutral-500 hover:text-forest-dark"
              )}
            >
              {l.label}
              {active === l.id && (
                <span className="absolute -bottom-1 left-0 right-0 h-px bg-forest" />
              )}
            </button>
          ))}
          <a
            href={profile.resumeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center h-9 px-4 rounded-md bg-brand-gradient text-white text-[13px] font-medium hover:opacity-90 transition-opacity"
          >
            Resume
          </a>
        </nav>

        {/* Mobile toggle */}
        <button
          onClick={() => setOpen(!open)}
          className="md:hidden w-10 h-10 grid place-items-center rounded-md hover:bg-neutral-100"
          aria-label="Toggle menu"
        >
          <div className="flex flex-col gap-[5px] w-5">
            <span className={cn("h-px bg-neutral-700 transition-all", open && "rotate-45 translate-y-[6px]")} />
            <span className={cn("h-px bg-neutral-700 transition-all", open && "opacity-0")} />
            <span className={cn("h-px bg-neutral-700 transition-all", open && "-rotate-45 -translate-y-[6px]")} />
          </div>
        </button>
      </div>

      {/* Mobile menu */}
      <div
        className={cn(
          "md:hidden overflow-hidden transition-all duration-300 bg-white/95 backdrop-blur-md border-b border-neutral-200",
          open ? "max-h-96" : "max-h-0 border-b-0"
        )}
      >
        <nav className="flex flex-col px-6 py-2">
          {links.map((l) => (
            <button
              key={l.id}
              onClick={() => go(l.id)}
              className={cn(
                "text-left py-3 text-[15px] border-b border-neutral-100 last:border-0",
                active === l.id ? "text-forest-dark font-medium" : "text-neutral-600"
              )}
            >
              {l.label}
            </button>
          ))}
          <a
            href={profile.resumeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 mb-2 inline-flex items-center justify-center h-10 rounded-md bg-brand-gradient text-white text-[14px] font-medium"
          >
            Resume
          </a>
        </nav>
      </div>
    </header>
  );
};

export default Nav;
