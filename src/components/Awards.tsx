import { Award as AwardIcon } from "lucide-react";
import Section from "@/components/Section";
import { awards } from "@/data/profile";

const Awards = () => {
  return (
    <Section id="awards" eyebrow="Awards" title="Honors & achievements">
      <div className="grid sm:grid-cols-2 gap-4">
        {awards.map((award, i) => (
          <div
            key={i}
            className="flex items-start gap-4 rounded-xl border border-neutral-200 p-5 hover:border-forest/40 transition-colors"
          >
            <span className="mt-0.5 shrink-0 w-9 h-9 rounded-lg bg-forest/[0.08] text-forest grid place-items-center">
              <AwardIcon size={18} strokeWidth={1.75} />
            </span>
            <div>
              <h3 className="text-[15px] font-semibold text-neutral-900 leading-snug">
                {award.title}
              </h3>
              <p className="mt-1 text-[13px] text-neutral-500">
                {award.issuer}
                {award.year && ` · ${award.year}`}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
};

export default Awards;
