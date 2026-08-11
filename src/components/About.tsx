import Section from "@/components/Section";
import { profile } from "@/data/profile";

const About = () => {
  return (
    <Section id="about" eyebrow="About" title="A bit about me">
      <div className="grid md:grid-cols-[1.6fr_1fr] gap-10">
        <div className="space-y-5 text-[16px] leading-[1.7] text-neutral-700">
          {profile.about.map((para, i) => (
            <p key={i}>{para}</p>
          ))}
        </div>

        <aside className="rounded-xl border border-neutral-200 bg-neutral-50/60 p-6 h-fit">
          <ul className="space-y-4">
            {profile.quickFacts.map((fact) => (
              <li key={fact.label}>
                <p className="text-[12px] font-medium tracking-[0.14em] uppercase text-forest">
                  {fact.label}
                </p>
                <p className="mt-1 text-[15px] text-neutral-800">{fact.value}</p>
              </li>
            ))}
          </ul>
        </aside>
      </div>
    </Section>
  );
};

export default About;
