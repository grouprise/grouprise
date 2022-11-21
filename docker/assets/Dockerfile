FROM node:lts-alpine AS grouprise-assets
WORKDIR /root/assets
ADD package.json package-lock.json ./
RUN ADBLOCK=true npm ci && npx browserslist@latest --update-db
ADD res/ ./res/
ADD .eslintrc.js webpack.config.js ./
CMD ["npm", "run", "dev"]
