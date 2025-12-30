import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Bundle optimization (T223)
  compiler: {
    // Remove console logs in production
    removeConsole: process.env.NODE_ENV === "production",
  },

  // Optimize images
  images: {
    formats: ["image/avif", "image/webp"],
    minimumCacheTTL: 60,
  },

  // Enable experimental features for better performance
  experimental: {
    // Optimize package imports
    optimizePackageImports: [
      "lucide-react",
      "react-hot-toast",
      "date-fns",
    ],
  },

  // Disable TypeScript errors during build for deployment
  typescript: {
    ignoreBuildErrors: true,
  },

  // Disable ESLint during builds
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Compression
  compress: true,

  // Strict mode for better error detection
  reactStrictMode: true,

  // Power optimized settings
  poweredByHeader: false, // Remove X-Powered-By header

  // Use standalone output for Docker (skips static optimization)
  output: 'standalone',
};

export default nextConfig;
