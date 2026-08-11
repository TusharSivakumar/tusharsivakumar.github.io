import Section from "@/components/Section";
import { experience } from "@/data/profile";

const Experience = () => {
  return (
    <Section id="experience" eyebrow="Experience" title="Where I've been">
      <div className="relative">
        {/* vertical line */}
        <span className="absolute left-[7px] top-2 bottom-2 w-px bg-neutral-200 sm:left-[9px]" />

        <div className="space-y-10">
          {experience.map((item, i) => (
            <div key={i} className="relative pl-8 sm:pl-10">
              {/* dot */}
              <span className="absolute left-0 top-1.5 w-[15px] h-[15px] rounded-full border-2 border-forest bg-white sm:w-[19px] sm:h-[19px]" />
              <span className="absolute left-[4px] top-[10px] w-[7px] h-[7px] rounded-full bg-forest sm:left-[6px] sm:top-[12px]" />

              <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                <h3 className="text-[17px] font-semibold text-neutral-900">
                  {item.role}
                  <span className="text-neutral-400 font-normal"> · </span>
                  <span className="text-forest font-medium">{item.org}</span>
                </h3>
                <span className="text-[13px] text-neutral-500 tabular-nums">
                  {item.period}
                </span>
              </div>

              <p className="mt-2 text-[15px] leading-[1.65] text-neutral-600 max-w-2xl">
                {item.description}
              </p>

              {item.tags && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[12px] text-neutral-500 border border-neutral-200 rounded px-2 py-0.5"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
};

export default Experience;
