import { Metadata } from "next";

export const metadata: Metadata = {
    title: "K-Food Leaderboard | Trending Korean Snacks & Ramen",
    description: "Discover the top trending Korean ramen, snacks, and beverages from convenience stores. Real-time rankings updated daily.",
    keywords: ["K-Food", "Korean Snacks", "Korean Ramen", "Korean Beverages", "GS25", "CU", "Convenience Store"],
    openGraph: {
        title: "K-Food Leaderboard | Trending Korean Snacks",
        description: "Real-time rankings of the hottest Korean snacks and ramen from convenience stores",
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
        title: "K-Food Leaderboard | Korean Snacks Rankings",
        description: "Discover trending Korean ramen, snacks, and drinks",
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
