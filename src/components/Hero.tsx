import { ArrowDown } from "lucide-react";
import SocialLinks from "@/components/SocialLinks";
import { profile } from "@/data/profile";

const Hero = () => {
  const scrollTo = (id: string) =>
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });

  return (
    <section
      id="home"
      className="relative min-h-[92vh] flex items-center overflow-hidden"
    >
      {/* Ambient background wash */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-24 -right-24 w-[36rem] h-[36rem] rounded-full bg-forest/[0.06] blur-3xl" />
        <div className="absolute -bottom-32 -left-24 w-[32rem] h-[32rem] rounded-full bg-forest/[0.05] blur-3xl" />
        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, #2563eb 1px, transparent 0)",
            backgroundSize: "28px 28px",
          }}
        />
      </div>

      <div className="max-w-5xl mx-auto px-6 sm:px-8 w-full grid md:grid-cols-[1.4fr_1fr] gap-12 md:gap-10 items-center pt-24 pb-16">
        {/* Left: text */}
        <div className="animate-hero">
          <p className="text-[14px] font-medium tracking-[0.18em] uppercase text-forest mb-5">
            {profile.tagline}
          </p>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gradient tracking-tight leading-[1.02]">
            {profile.name}
            <span className="text-gradient">.</span>
          </h1>
          <p className="mt-6 text-[17px] sm:text-[18px] leading-[1.6] text-neutral-700 max-w-xl">
            {profile.hero.blurb}
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <button
              onClick={() => scrollTo("projects")}
              className="inline-flex items-center h-11 px-6 rounded-md bg-brand-gradient text-white text-[15px] font-medium hover:opacity-90 transition-opacity"
            >
              View my work
            </button>
            <button
              onClick={() => scrollTo("contact")}
              className="inline-flex items-center h-11 px-6 rounded-md border border-neutral-300 text-neutral-700 text-[15px] font-medium hover:border-forest hover:text-forest transition-colors"
            >
              Get in touch
            </button>
          </div>

          <div className="mt-9">
            <SocialLinks size={22} />
          </div>
        </div>

        {/* Right: headshot */}
        <div className="flex justify-center md:justify-end animate-hero-delay">
          <div className="relative">
            <div className="absolute inset-0 rounded-full bg-forest/10 blur-2xl scale-95" />
            <img
              src={profile.headshot}
              alt={profile.name}
              className="relative w-60 h-60 sm:w-72 sm:h-72 md:w-80 md:h-80 rounded-full object-cover border-4 border-white shadow-xl bg-neutral-100"
            />
          </div>
        </div>
      </div>

      {/* Scroll cue */}
      <button
        onClick={() => scrollTo("about")}
        aria-label="Scroll to about"
        className="absolute bottom-8 left-1/2 -translate-x-1/2 text-neutral-400 hover:text-forest transition-colors animate-bounce-slow"
      >
        <ArrowDown size={22} />
      </button>
    </section>
  );
};

export default Hero;
