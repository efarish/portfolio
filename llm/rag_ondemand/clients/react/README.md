# React + Vite

This React project was created using the following Node.js command and selecting a React JavaScript template.

```bash 
npm create vite@latest
```

Inside the project directory created (`react` in this case), run the following,

```bash
npm install
npm run dev
```

The output of the last command should contain a browser link to the application.

The default config file for the React app is found in the `./public` directory. In it is a the `config.json` containing the URL for the Rag OnDemand microservice which points to localhost. This file gets overwritten when the app is deployed by create CI/CD pipeline found in the `cloudformation` directory. To start a local instance of the microservice, see this `./src/build_docker.sh` script for the command to get a Docker instance running.

