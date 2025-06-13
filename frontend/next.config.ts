import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/table-retriever",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://localhost:8000/api/table-retriever"
            : "/api/table-retriever",
      },
    ];
  },
};

export default nextConfig;
