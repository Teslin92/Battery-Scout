import { Newspaper, Brain, Globe } from "lucide-react";

const features = [
  {
    icon: Newspaper,
    title: "Curated Daily",
    description:
      "Hand-picked relevant news from global sources. No noise, just the stories that matter to battery industry professionals.",
  },
  {
    icon: Brain,
    title: "AI Summaries",
    description:
      "Quick insights without information overload. Each article comes with an AI-generated summary so you can decide what's worth your time.",
  },
  {
    icon: Globe,
    title: "Global Coverage",
    description:
      "Including translated Chinese industry news. Access insights from CATL, BYD, and other major players often missed by Western media.",
  },
];

export const FeaturesSection = () => {
  return (
    <section className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Why Battery Brief?
          </h2>
          <p className="text-lg text-muted-foreground">
            Stay informed without the information overload
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {features.map((feature, index) => (
            <div
              key={index}
              className="text-center p-8 rounded-2xl bg-card border border-border/50 card-hover animate-fade-in"
              style={{ animationDelay: `${index * 0.15}s` }}
            >
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-teal/10 mb-6">
                <feature.icon className="w-8 h-8 text-accent" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                {feature.title}
              </h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
