import { Github, ArrowUpRight } from "lucide-react";
import Section from "@/components/Section";
import { projects, type Project } from "@/data/profile";

const openLink = (p: Project) => {
  if (p.link) window.open(p.link, "_blank", "noopener,noreferrer");
};

const Projects = () => {
  return (
    <Section id="projects" eyebrow="Projects" title="Things I've built">
      <div className="grid sm:grid-cols-2 gap-6">
        {projects.map((project, i) => (
          <article
            key={i}
            onClick={() => openLink(project)}
            className={`group flex flex-col rounded-xl border border-neutral-200 overflow-hidden hover:border-forest/40 hover:shadow-md transition-all duration-300 ${
              project.link ? "cursor-pointer" : ""
            }`}
          >
            {/* Preview */}
            <div className="aspect-[16/9] bg-neutral-100 flex items-center justify-center overflow-hidden">
              {project.image ? (
                <img
                  src={project.image}
                  alt={project.title}
                  className="w-full h-full object-cover group-hover:scale-[1.04] transition-transform duration-500"
                />
              ) : (
                <div className="text-5xl select-none opacity-90">
                  {project.emoji ?? "\u{1F4E6}"}
                </div>
              )}
            </div>

            {/* Body */}
            <div className="flex flex-col flex-1 p-5">
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-[17px] font-semibold text-neutral-900 group-hover:text-forest-dark transition-colors">
                  {project.title}
                </h3>
                {project.link && (
                  <ArrowUpRight
                    size={18}
                    className="text-neutral-400 group-hover:text-forest transition-colors shrink-0"
                  />
                )}
              </div>

              {project.badge && (
                <span className="mt-1 self-start text-[12px] font-medium text-forest bg-forest/[0.06] rounded px-2 py-0.5">
                  {project.badge}
                </span>
              )}

              <p className="mt-3 text-[14.5px] leading-[1.6] text-neutral-600 flex-1">
                {project.description}
              </p>

              <div className="mt-4 flex items-center justify-between gap-3">
                <div className="flex flex-wrap gap-x-3 gap-y-1 text-[12.5px] text-neutral-500">
                  {project.technologies.map((t) => (
                    <span key={t}>{t}</span>
                  ))}
                </div>
                {project.github && (
                  <a
                    href={project.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    aria-label="GitHub repository"
                    className="text-neutral-400 hover:text-forest transition-colors shrink-0"
                  >
                    <Github size={17} strokeWidth={1.5} />
                  </a>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>
    </Section>
  );
};

export default Projects;
