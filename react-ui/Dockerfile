FROM node:alpine AS react
WORKDIR /react
COPY package* tsconfig.json ./
RUN npm install --omit=dev
COPY public ./public
COPY src ./src
RUN npm run build

FROM backend AS django

FROM nginx:alpine
WORKDIR /etc/nginx
RUN rm nginx.conf conf.d/default.conf
COPY nginx/conf/nginx.conf nginx.conf
COPY --from=react /react/build /var/www
COPY --from=django /django/static /var/www/static