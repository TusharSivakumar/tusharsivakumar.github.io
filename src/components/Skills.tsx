import Section from "@/components/Section";
import { skills } from "@/data/profile";

const Skills = () => {
  return (
    <Section id="skills" eyebrow="Skills" title="What I work with">
      <div className="grid sm:grid-cols-2 gap-6">
        {skills.map((group) => (
          <div
            key={group.category}
            className="rounded-xl border border-neutral-200 p-6 hover:border-forest/40 transition-colors"
          >
            <h3 className="text-[15px] font-semibold text-forest-dark mb-4">
              {group.category}
            </h3>
            <div className="flex flex-wrap gap-2">
              {group.items.map((item) => (
                <span
                  key={item}
                  className="inline-flex items-center px-3 py-1.5 rounded-full bg-forest/[0.06] text-forest text-[13px] font-medium"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
};

export default Skills;
