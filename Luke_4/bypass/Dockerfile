FROM node:18-alpine AS base
WORKDIR /app
COPY bypass ./
COPY flag.txt* /app/flag.txt 
RUN npm install && npm run build

ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
RUN chown nextjs:nodejs /app/.next/standalone /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", ".next/standalone/server.js"]
