import { profile } from "@/data/profile";

const Footer = () => {
  return (
    <footer className="border-t border-neutral-200 py-8">
      <div className="max-w-5xl mx-auto px-6 sm:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-[13.5px] text-neutral-500">
        <p>
          © {new Date().getFullYear()} {profile.name}
        </p>
        <p>
          Built with React, TypeScript &amp; Tailwind ·{" "}
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="hover:text-forest transition-colors"
          >
            Back to top ↑
          </button>
        </p>
      </div>
    </footer>
  );
};

export default Footer;
