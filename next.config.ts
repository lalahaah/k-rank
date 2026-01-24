import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "image.oliveyoung.co.kr",
      },
      {
        protocol: "https",
        hostname: "dnm.nflximg.net",
      },
      {
        protocol: "https",
        hostname: "assets.nflxext.com",
      },
      {
        protocol: "https",
        hostname: "places.googleapis.com",
      },
    ],
  },
};

export default nextConfig;
