FROM node:latest
RUN mkdir -p /usr/src/app1
WORKDIR /usr/src/app1
COPY package.json /usr/src/app1/
RUN npm install
COPY . /usr/src/app1
EXPOSE 3000
CMD [ “npm”, “start” ]