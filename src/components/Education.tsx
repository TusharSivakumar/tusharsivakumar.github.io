import Section from "@/components/Section";
import { education } from "@/data/profile";

const Education = () => {
  return (
    <Section id="education" eyebrow="Education" title="Where I've studied">
      <div className="space-y-6">
        {education.map((item, i) => (
          <div
            key={i}
            className="rounded-xl border border-neutral-200 p-6 hover:border-forest/40 transition-colors"
          >
            <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
              <h3 className="text-[17px] font-semibold text-neutral-900">
                {item.school}
              </h3>
              <span className="text-[13px] text-neutral-500 tabular-nums">
                {item.period}
              </span>
            </div>
            <p className="mt-1 text-[14.5px] font-medium text-forest">
              {item.credential}
            </p>
            {item.description && (
              <p className="mt-3 text-[14.5px] leading-[1.6] text-neutral-600">
                {item.description}
              </p>
            )}
            {item.highlights && (
              <div className="mt-4 flex flex-wrap gap-2">
                {item.highlights.map((h) => (
                  <span
                    key={h}
                    className="inline-flex items-center px-3 py-1 rounded-full bg-forest/[0.06] text-forest text-[12.5px] font-medium"
                  >
                    {h}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </Section>
  );
};

export default Education;
