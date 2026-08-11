import { Mail, Linkedin } from "lucide-react";
import { useReveal } from "@/hooks/useReveal";
import SocialLinks from "@/components/SocialLinks";
import { profile } from "@/data/profile";
import { cn } from "@/lib/utils";

const Contact = () => {
  const { ref, visible } = useReveal<HTMLElement>();
  const email = profile.socials.email;

  return (
    <section
      id="contact"
      ref={ref}
      className={cn("scroll-mt-24 py-24 reveal", visible && "reveal-in")}
    >
      <div className="rounded-2xl bg-brand-gradient text-white px-8 sm:px-12 py-14 text-center relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, #ffffff 1px, transparent 0)",
            backgroundSize: "26px 26px",
          }}
        />
        <div className="relative">
          <p className="text-[13px] font-medium tracking-[0.18em] uppercase text-white/70 mb-4">
            Contact
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
            Let's build something.
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-white/85 max-w-lg mx-auto">
            I'm always open to interesting projects, collaborations, and
            conversations. Reach out any time.
          </p>

          {email ? (
            <a
              href={`mailto:${email}`}
              className="mt-8 inline-flex items-center gap-2 h-12 px-7 rounded-md bg-white text-forest text-[15px] font-semibold hover:bg-neutral-100 transition-colors"
            >
              <Mail size={18} />
              {email}
            </a>
          ) : (
            <a
              href={profile.socials.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-8 inline-flex items-center gap-2 h-12 px-7 rounded-md bg-white text-forest text-[15px] font-semibold hover:bg-neutral-100 transition-colors"
            >
              <Linkedin size={18} />
              Connect on LinkedIn
            </a>
          )}

          <div className="mt-8 flex justify-center [&_a]:text-white/70 [&_a:hover]:text-white">
            <SocialLinks size={22} />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
