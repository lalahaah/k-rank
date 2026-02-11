import { Metadata } from "next";

export const metadata: Metadata = {
    title: "K-Food Leaderboard | Trending Seoul Restaurants",
    description: "Discover the hottest trending restaurants, cafes, and bars in Seoul. Real-time rankings based on local hype and global interest.",
    keywords: ["K-Food", "Seoul Restaurants", "Trending Restaurants", "Korean Dining", "Seoul Eats", "Hot Places Korea"],
    openGraph: {
        title: "K-Food Leaderboard | Trending Seoul Restaurants",
        description: "Explore the most popular restaurants and cafes in Seoul right now.",
        type: "website",
        url: "https://k-rank.vercel.app/food",
        images: [
            {
                url: "/og-food.png",
                width: 1200,
                height: 630,
                alt: "K-Food Leaderboard",
            },
        ],
    },
    twitter: {
        card: "summary_large_image",
        title: "K-Food Leaderboard | Seoul Restaurant Rankings",
        description: "Discover trending Seoul restaurants and local dining favorites.",
        images: ["/og-food.png"],
    },
};

export default function FoodLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
