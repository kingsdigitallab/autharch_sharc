# Shakespeare Holdings in the Royal Collection

This project is forked from https://github.com/kingsdigitallab/gpp-vue.

## Local development

To run this project locally:

1. Install [Node](https://nodejs.org/en/download/). Consider using Homebrew to install Node if you are on a Mac.
2. Clone this repository
3. Add a file called `.env` at the root of the project
   - Add the AuthArch API URL `VUE_APP_API_URL = 'http...'` (defaults to Django development URL)
   - and the AuthArch API key for the project `VUE_APP_API_TOKEN = 'API-KEY-VALUE'`
4. Run `npm install` to install the project dependencies
5. Run `npm run serve` to run the local server
6. The app should be available at http://localhost:8080/
