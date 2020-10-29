[![Issues][issues]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
![github-shield]
[![License][license-shield]][license-url]

<br />
<p align="center">
  <a href="https://github.com/shridpant/stockie">
    <img src="static/readme/title_icon.png" alt="Logo" width="200" height="75">
  </a>
  
  <h3 align="center">Stockie</h3>

  <p align="center">
    Welcome to the GitHub repository of Stokie! Stockie is an open source project distributed under the `MIT License`.
    <br />
    <a href="https://github.com/shridpant/stockie/blob/main/README.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/shridpant/stockie/issues">Report Bug</a>
    ·
    <a href="https://github.com/shridpant/stockie/issues">Request Feature</a>
  </p>
</p>


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
    * [Built With](#built-with)
    * [Usage](#usage)
* [Features](#features)
* [Contrubuting](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledements](#acknowledements)

<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screenshot][product-screenshot]](https://github.com/shridpant/stockie)

This repository contains the source code for *Stockie*- an investment portfolio management web application. The state-of-the-art recommendation engine provides real-time personalized insights for its users. Analysis of tweets, relevant news, the stocks' historic performances and many other parameters are evaluated for *the most up-to-date* insights. Besides this, the users may visit eachother's profiles!

### Built With

The server-side application was built with Flask and Socket.IO. Other resources included SQLite3 for database management, and HTML, CSS and JavaScript for the client-side application. Stockie was made possible by [many](#acknowledements) open-sourced libraries and frameworks.

### Usage

The web interface is simple and easy to use. After a one-step registration process, the users may log in and immediately start trading stocks. Each user is provided with $10,000/- cash at the start, which the users may utilize to trade stocks. To execute, simply:

1. Clone this repository with `git clone https://github.com/shridpant/stockie`. Please ensure that you have all the dependencies from `requirements.txt` installed.
2. Start your server with `python app.py`.
3. Open the address from your terminal on your browser. And you're all set!

## Features

Stockie provides state-of-the-art stock analysis tools to its users. This includes up-to-date performance metrics from trusted sources, real-time tweet and news insights, and a recommender engine based on the stocks' historic data. An example of the insights:

[![Insights Screenshot][insights-screenshot]](https://github.com/shridpant/stockie)

If a registered `stock symbol` was entered as a search query, a request is made via yfinance for additional information. The user is, then, provided a link to a dynamically created company profile for additional insights. An example of the `company profile `: 

[![Company Profile Screenshot][company-screenshot]](https://github.com/shridpant/stockie)

The users may connect with one another to engage in relevant discussions. Each user maintains a public profile bearing public contact information. The users may search and visit each other's profiles to chat/email/phone. An example of this profile:

[![Profile Screenshot][profile-screenshot]](https://github.com/shridpant/stockie)

## Contributing

This project welcomes contributions and suggestions. Feel free to fork this repository or submit your ideas through [issues](https://github.com/shridpant/stockie/issues).

### Usage

To execute, simply:

1. Clone this repository with `git clone https://github.com/shridpant/stockie`. 
2. Navigate to the root folder of the project and execute `pip install -r requirements.txt` to install all dependencies.
3. Start your server with `python app.py`.
4. Open the address from your terminal on your browser. And you're all set!

<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE](https://github.com/shridpant/stockie/blob/main/LICENSE) for more information.

<!-- CONTACT -->
## Contact

Feel free to hmu on my [LinkedIn](https://www.linkedin.com/in/shridpant/)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledements

Stockie wouldn't be possible without the following resources:

* [Twitter](https://developer.twitter.com/en)
* [yfinance](https://github.com/ranaroussi/yfinance)
* [IEX](https://iextrading.com/developer)
* [News API](https://newsapi.org/)
* [CS50](https://cs50.harvard.edu/)
* [Chart.js](https://www.chartjs.org/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Jupyter Notebook](https://jupyter.org/)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)
* [Google Fonts](https://fonts.google.com/)
* [Img Shields](https://shields.io)

<!-- MARKDOWN LINKS & IMAGES -->
[issues]: https://img.shields.io/github/issues-raw/shridpant/stockie
[issues-url]: https://github.com/shridpant/stockie/issues
[license-shield]: https://img.shields.io/apm/l/vim-mode
[license-url]: https://github.com/shridpant/stockie/blob/master/LICENSE
[linkedin-shield]: static/readme/linkedin.svg
[linkedin-url]: https://www.linkedin.com/in/shridpant/
[github-shield]: https://img.shields.io/github/followers/shridpant?style=social
[product-screenshot]: static/readme/screenshot.PNG
[insights-screenshot]: static/readme/insights-screenshot.PNG
[company-screenshot]: static/readme/company-screenshot.PNG
[profile-screenshot]: static/readme/profile-screenshot.PNG
