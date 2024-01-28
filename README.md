# paperboy

```
usage: paperboy.py [-h] [-l MINYEAR] [-u MAXYEAR] [-r] [-s] module cookie

Get Maynooth University exam papers.

positional arguments:
  module                the code of the module you want papers for e.g. 'CS211'
  cookie                a JSON file with the key and value of your session cookie OR the key and value as separated by '='

options:
  -h, --help            show this help message and exit
  -l MINYEAR, --minyear MINYEAR
                        the inclusive lower bound of the range of years you want papers for
  -u MAXYEAR, --maxyear MAXYEAR
                        the non-inclusive upper bound of the range of years you want papers for
  -r, --noresits        exclude papers from Autumn exam periods
  -s, --save            save the exam papers to current working directory instead of printing links to stdout
```

The `cookie` argument is a path to a JSON file containing the name and value of your session cookie for the exam papers site. The site uses this cookie to authenticate you. Follow the steps below to get this cookie:

1. In Chrome, log in to the 
   [exam papers website](https://www.maynoothuniversity.ie/library/exam-papers)

2. Press F12 to open Developer Tools and go to the Application tab

3. Go to `Cookies` > `https://www.maynoothuniversity.ie` and copy and paste the name and value
   of the session cookie into your cookie file

This cookie will expire after some time and you will need to follow these steps again.

**Don't share this cookie with anyone or accidentally push it to a repo**

![Chrome Developer Tools screenshot](images/devtools.png)

#### Example cookie file
```json
{
    "COOKIE_NAME": "COOKIE_VALUE"
}
```