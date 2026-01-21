import { ExternalLink } from "lucide-react";

interface ArticleCardProps {
  flag: string;
  source: string;
  title: string;
  summary: string;
  category: string;
  categoryColor: string;
  url?: string;
}

const categoryColorMap: Record<string, string> = {
  industry: "bg-category-industry",
  technology: "bg-category-technology",
  supply: "bg-category-supply",
  manufacturing: "bg-category-manufacturing",
  policy: "bg-category-policy",
  recycling: "bg-category-recycling",
  market: "bg-category-market",
};

export const ArticleCard = ({
  flag,
  source,
  title,
  summary,
  category,
  categoryColor,
  url = "#",
}: ArticleCardProps) => {
  return (
    <article className="bg-card rounded-xl p-6 shadow-md card-hover border border-border/50">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="text-lg">{flag}</span>
          <span className="font-medium">{source}</span>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium text-white ${categoryColorMap[categoryColor] || "bg-primary"}`}
        >
          {category}
        </span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-foreground mb-3 line-clamp-2">
        {title}
      </h3>

      {/* AI Summary */}
      <p className="text-muted-foreground text-sm mb-4 line-clamp-3">
        {summary}
      </p>

      {/* Read More Link */}
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:text-accent/80 transition-colors"
      >
        Read More
        <ExternalLink className="w-3 h-3" />
      </a>
    </article>
  );
};
