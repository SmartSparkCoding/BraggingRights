# BraggingRights

## What and Why

Bragging Rights is designed by me to solve a very specific problem in our house - who is winning? We always wanted to know who was winning the competitions in our board games. To make it good, we have leaderboards and competitions that also help keep track of what prizes people will win. It keeps tracks of games and everything. It has a /admin route, /up and even /updates.xml which is very new to me, very simply leaning this towards a full stack app. I'm looking forward to making a proper public full-stack app soon!

## How does it work?

To run the app, you need to install the requirements found in requirements.txt, then run python3 app.py. To have fake data to be inserted, just run python3 seed_data.py to insert random data. The app runs on my Hack Club Nest and uses Hack Club CDN to host the logo because IT IS FASTER!

## AI Declaration

I used 2 types of AI in my project. The first and main one was ChatGPT. I used ChatGPT to learn a lot about the routes, and databases simply because I don't know very much about databases and how this works. The only 'copy and pasted' code in this project is the admin stuff (and another file mentioned later) as this included a massive amount of POST / GET requests to the database and making sure that I am not just going to wipe the database.....

The other AI I used was GitHub Copilot, but I ran out of token very quickly. But when I had tokens, it helped me with add-game! Although it broke, so I had to fix the issue manually.

## What does the App Use

It uses Flask, and SQLite DB, part of Flask. It also uses static HTML/CSS/JS for obviously the actual site. yeah thats it ig?

## License

MIT License

Copyright (c) 2026 Jacob Navaratne

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
