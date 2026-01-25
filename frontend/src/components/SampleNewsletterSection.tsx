import { useQuery } from "@tanstack/react-query";
import { ArticleCard } from "./ArticleCard";
import { getSampleContent } from "@/lib/api";

const categoryColorMap: Record<string, string> = {
  "Industry News": "industry",
  "Technology & Innovation": "technology",
  "Supply Chain & Materials": "supply",
  "Manufacturing & Production": "manufacturing",
  "Policy & Regulations": "policy",
  "Battery Recycling": "recycling",
  "Market Applications": "market",
};

export const SampleNewsletterSection = () => {
  const { data: contentResponse, isLoading, isError, error } = useQuery({
    queryKey: ["sample-content"],
    queryFn: async () => {
      return await getSampleContent();
    },
    retry: 2, // Retry twice on failure
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
  });

  const articles = contentResponse?.sample_articles || [];

  return (
    <section className="py-20 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            What You'll Get
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Here's a preview from this week — curated insights delivered
            straight to your inbox
          </p>
        </div>

        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="bg-card rounded-xl p-6 shadow-md animate-pulse"
              >
                <div className="h-4 bg-muted rounded w-1/3 mb-3" />
                <div className="h-6 bg-muted rounded w-full mb-3" />
                <div className="h-4 bg-muted rounded w-full mb-2" />
                <div className="h-4 bg-muted rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : isError ? (
          <div className="text-center text-muted-foreground py-12">
            <p className="text-destructive mb-2">Unable to load sample articles.</p>
            <p className="text-sm">
              {error instanceof Error ? error.message : "Please try refreshing the page."}
            </p>
          </div>
        ) : articles.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {articles.map((article, index) => (
              <div
                key={index}
                className="animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <ArticleCard
                  flag={article.source_country || ""}
                  source={article.source_name || "Unknown"}
                  title={article.title}
                  summary={article.summary}
                  category={article.category}
                  categoryColor={categoryColorMap[article.category] || "industry"}
                  url={article.url || "#"}
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-muted-foreground py-12">
            No sample articles available at the moment.
          </div>
        )}
      </div>
    </section>
  );
};
