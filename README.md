---
### ⚠ Disclaimer ⚠ <br/>

All the code of this project is open-source. However, at the moment it will not work as well as in 2021 due to the redesign of the Csgorun and Steam system <br/>

The author condemns any gambling-related activity

---
### ▷ Description <br/>
&emsp;There are many casino-related websites.<br/>
&emsp;One of them (let's call csgorun) gives its users a promo code for N amount of money every day.<br/>
&emsp;I took advantage of this opportunity by implementing this project.<br/>

### ▷ The main goal of the project <br/>
&emsp;*Parse* a promo code from sources and automatically *activate* it from a large number of accounts

### ▷ Expenses and profit <br/>
&emsp;It took about a month to develop and test the system, as I had to do other things in parallel. <br/>
&emsp;The total cost of the project (proxy/accounts/captcha) ~ 140💲  <br/>
&emsp;Total net profit ~ 1000💲<br/>

---
### ☰ The project consists of 11 parts (***Project-Eleven***):

- Steam authentication via selenium (Steamauth.py)
- Account Setup (AccsSetup.py)
- Receiving cookies for each account (GetCookies.py)
- Performing actions on the account for further activation (Tesak.py)
- Parsing posts (VK/TG) with a promo code picture (GetPromo.py)
- Image processing for the most accurate recognition - Deprecated with rucaptcha
- Image text recognition (before - google cloud vision, now - rucaptcha)
- Promo code activation (ActivRun.py)
- Logging of the past activation
- Analyzing the received data and sending statistics to the telegram channel
- Transfer of the received currency to the wallet in automatic mode (Collect.py) - Deprecated

---
The interaction of all modules is implemented in a file Csgorun.py <br/>

### ☰ The main features of the project:

- Steam authentication module via selenium (personal development) - allows you to perform any actions from your account on the new and old versions of steam
- The program remembers its state and returns to it after restarting
- Each module is independent of other parts and is easily replaced/updated in case of any failures
- Fully automatic operation (turned on and forgot). The system itself will handle all errors related to the activation of the promo code.
- Simple extensibility. If desired, you can connect other activation sites or promo code sources to the system. You can also add more accounts.
- Analysability. The program provides statistics on any condition (errors in operation / number of activated accounts, etc.)
- Uniqueness. I know for sure that there are other people besides me who have done the same, but it is difficult to find a similar system on the Internet.

---
© I will not describe each module in detail (who needs it will figure it out). <br/>
© I just want to mention the fact that this is the second version of the code. <br/>
© It was developed after the site admins added a captcha during activation (which I successfully bypassed) <br/>
© I have found vulnerabilities in the current version of the site too, but I will not use it due to lack of time. <br/>

---
### ✅ YouRun, if you suddenly read it, thank you for the opportunity :) ✅
