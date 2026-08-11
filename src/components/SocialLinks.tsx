import { Github, Linkedin, Mail, Youtube } from "lucide-react";
import { profile } from "@/data/profile";

const XIcon = ({ size = 20 }: { size?: number }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width={size} height={size} fill="currentColor" aria-hidden="true">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

const SocialLinks = ({ size = 20, className = "" }: { size?: number; className?: string }) => {
  const { socials } = profile;
  const links = [
    socials.github && { href: socials.github, label: "GitHub", icon: (p: { size?: number }) => <Github {...p} strokeWidth={1.5} /> },
    socials.linkedin && { href: socials.linkedin, label: "LinkedIn", icon: (p: { size?: number }) => <Linkedin {...p} strokeWidth={1.5} /> },
    socials.email && { href: `mailto:${socials.email}`, label: "Email", icon: (p: { size?: number }) => <Mail {...p} strokeWidth={1.5} /> },
    socials.youtube && { href: socials.youtube, label: "YouTube", icon: (p: { size?: number }) => <Youtube {...p} strokeWidth={1.5} /> },
    socials.x && { href: socials.x, label: "X (Twitter)", icon: (p: { size?: number }) => <XIcon {...p} /> },
  ].filter(Boolean) as { href: string; label: string; icon: (p: { size?: number }) => JSX.Element }[];

  return (
    <div className={`flex items-center gap-6 ${className}`}>
      {links.map(({ href, label, icon: Icon }) => {
        const isMail = href.startsWith("mailto:");
        return (
          <a
            key={label}
            href={href}
            target={isMail ? undefined : "_blank"}
            rel={isMail ? undefined : "noopener noreferrer"}
            aria-label={label}
            className="text-neutral-500 hover:text-forest transition-colors duration-200"
          >
            <Icon size={size} />
          </a>
        );
      })}
    </div>
  );
};

export default SocialLinks;
