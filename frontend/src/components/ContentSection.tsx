import {
  Building2,
  Scale,
  Truck,
  Atom,
  FlaskConical,
  Recycle,
} from "lucide-react";

const categories = [
  {
    icon: Building2,
    title: "Companies & Deals",
    description:
      "M&A activity, funding rounds, IPOs, and strategic partnerships shaping the battery landscape.",
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    icon: Scale,
    title: "Policy & Regulation",
    description:
      "Government incentives, trade policies, environmental regulations, and compliance updates.",
    color: "text-secondary",
    bgColor: "bg-secondary/10",
  },
  {
    icon: Truck,
    title: "Supply Chain",
    description:
      "Raw materials, mining developments, logistics challenges, and supply security analysis.",
    color: "text-accent",
    bgColor: "bg-accent/10",
  },
  {
    icon: Atom,
    title: "Lithium-ion & Solid-state",
    description:
      "Technology advances, performance improvements, and manufacturing breakthroughs.",
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    icon: FlaskConical,
    title: "Sodium-ion & Alternatives",
    description:
      "Emerging chemistries, research milestones, and commercialization progress.",
    color: "text-secondary",
    bgColor: "bg-secondary/10",
  },
  {
    icon: Recycle,
    title: "Recycling & Second-life",
    description:
      "Battery recycling innovations, circular economy initiatives, and repurposing strategies.",
    color: "text-accent",
    bgColor: "bg-accent/10",
  },
];

export function ContentSection() {
  return (
    <section className="py-20 bg-background">
      <div className="container px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
            What We Cover
          </h2>
          <p className="text-lg text-muted-foreground">
            Comprehensive coverage across all battery industry verticals, 
            tailored to your interests and delivered to your inbox.
          </p>
        </div>

        {/* Categories Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {categories.map((category, index) => (
            <div
              key={category.title}
              className="group p-6 rounded-xl bg-card border border-border hover:shadow-lg hover:border-primary/30 transition-all duration-300"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div
                className={`w-12 h-12 rounded-lg ${category.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}
              >
                <category.icon className={`w-6 h-6 ${category.color}`} />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                {category.title}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {category.description}
              </p>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
