/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  experimental: {
    instrumentationHook: false,
  }
}
module.exports = nextConfig