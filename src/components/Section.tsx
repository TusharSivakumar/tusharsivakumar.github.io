import { ReactNode } from "react";
import { useReveal } from "@/hooks/useReveal";
import { cn } from "@/lib/utils";

interface SectionProps {
  id: string;
  eyebrow: string;
  title: string;
  children: ReactNode;
  className?: string;
}

const Section = ({ id, eyebrow, title, children, className }: SectionProps) => {
  const { ref, visible } = useReveal<HTMLElement>();

  return (
    <section
      id={id}
      ref={ref}
      className={cn(
        "scroll-mt-24 py-20 sm:py-24 reveal",
        visible && "reveal-in",
        className
      )}
    >
      <div className="mb-10 sm:mb-12">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-[13px] font-medium tracking-[0.18em] uppercase text-forest">
            {eyebrow}
          </span>
          <span className="h-px flex-1 bg-neutral-200" />
        </div>
        <h2 className="text-3xl sm:text-4xl font-bold text-forest-dark tracking-tight">
          {title}
        </h2>
      </div>
      {children}
    </section>
  );
};

export default Section;
