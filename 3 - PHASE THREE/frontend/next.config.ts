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

  // Production optimizations
  swcMinify: true, // Use SWC for minification (faster than Terser)

  // Compression
  compress: true,

  // Strict mode for better error detection
  reactStrictMode: true,

  // Power optimized settings
  poweredByHeader: false, // Remove X-Powered-By header

  // Generate standalone output for Docker/serverless
  output: process.env.NODE_ENV === "production" ? "standalone" : undefined,
};

export default nextConfig;
